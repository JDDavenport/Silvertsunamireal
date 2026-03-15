# ACQUISITOR Production API
# FastAPI backend with PostgreSQL, Google OAuth, and multi-tenant security

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from functools import wraps
import os
import uuid
import json
import asyncpg
import httpx
import redis.asyncio as redis
from jose import JWTError, jwt
from passlib.context import CryptContext
import stripe
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID")
STRIPE_ENTERPRISE_PRICE_ID = os.getenv("STRIPE_ENTERPRISE_PRICE_ID")

# Initialize Stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Global connection pool and redis
pool: asyncpg.Pool = None
redis_client: redis.Redis = None

# Rate limit tiers
FREE_TIER = {"leads": 50, "emails": 25, "scrapes": 10}
PRO_TIER = {"leads": float('inf'), "emails": 500, "scrapes": 100}
ENTERPRISE_TIER = {"leads": float('inf'), "emails": float('inf'), "scrapes": float('inf')}

TIER_LIMITS = {
    "free": FREE_TIER,
    "pro": PRO_TIER,
    "enterprise": ENTERPRISE_TIER
}

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class GoogleAuthRequest(BaseModel):
    token: str
    email: str
    name: str
    picture: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    tier: str
    created_at: datetime


class LeadCreate(BaseModel):
    business_name: str
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_phone: Optional[str] = None
    industry: Optional[str] = None
    revenue: Optional[int] = None
    employees: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    pipeline_state: Optional[str] = None
    score: Optional[float] = None
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_phone: Optional[str] = None


class OutreachCreate(BaseModel):
    lead_id: str
    subject: str
    body: str
    message_type: str = "email"


class EmailProviderSetup(BaseModel):
    provider_type: str  # 'gmail', 'sendgrid', 'outlook'
    credentials: Dict[str, Any]


# ============================================================================
# BILLING MODELS
# ============================================================================

class CheckoutSessionRequest(BaseModel):
    tier: str  # 'pro' or 'enterprise'
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str


class SubscriptionResponse(BaseModel):
    tier: str
    status: str  # 'active', 'inactive', 'canceled', 'past_due'
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


class PortalSessionResponse(BaseModel):
    url: str


# ============================================================================
# AUTH & SECURITY FUNCTIONS
# ============================================================================

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current user from JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            uuid.UUID(user_id)
        )
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return dict(user)


# ============================================================================
# RATE LIMITING
# ============================================================================

def rate_limit(limit: int, per: str = "day", tier_field: str = "tier"):
    """Rate limiting decorator with tier support"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_id = str(current_user["id"])
            tier = current_user.get(tier_field, "free")
            
            # Get resource type from function name
            resource_type = func.__name__.replace("create_", "").replace("send_", "")
            
            # Check tier limits
            tier_limits = TIER_LIMITS.get(tier, FREE_TIER)
            tier_limit = tier_limits.get(resource_type, limit)
            
            # Unlimited for enterprise/pro on certain resources
            if tier_limit == float('inf'):
                return await func(*args, **kwargs)
            
            # Calculate window
            now = datetime.utcnow()
            if per == "day":
                window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif per == "hour":
                window_start = now.replace(minute=0, second=0, microsecond=0)
            else:
                window_start = now - timedelta(days=1)
            
            # Check rate limit in Redis
            rate_key = f"rate_limit:{user_id}:{resource_type}:{window_start.strftime('%Y%m%d')}"
            current_count = await redis_client.get(rate_key)
            
            if current_count and int(current_count) >= tier_limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Limit: {tier_limit} {per}. Upgrade your plan for more."
                )
            
            # Increment counter
            pipe = redis_client.pipeline()
            pipe.incr(rate_key)
            pipe.expire(rate_key, 86400)  # 24 hours
            await pipe.execute()
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_rate_limit_db(user_id: str, resource_type: str, tier: str = "free") -> bool:
    """Check rate limit using database (fallback if Redis unavailable)"""
    tier_limits = TIER_LIMITS.get(tier, FREE_TIER)
    tier_limit = tier_limits.get(resource_type, 50)
    
    if tier_limit == float('inf'):
        return True
    
    async with pool.acquire() as conn:
        # Get or create rate limit record
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        record = await conn.fetchrow(
            """SELECT * FROM rate_limits 
               WHERE user_id = $1 AND resource_type = $2 AND reset_at >= $3""",
            uuid.UUID(user_id), resource_type, today
        )
        
        if not record:
            # Create new record
            await conn.execute(
                """INSERT INTO rate_limits (user_id, resource_type, count, reset_at)
                   VALUES ($1, $2, 1, NOW() + INTERVAL '1 day')
                   ON CONFLICT (user_id, resource_type) 
                   DO UPDATE SET count = 1, reset_at = NOW() + INTERVAL '1 day'""",
                uuid.UUID(user_id), resource_type
            )
            return True
        
        if record["count"] >= tier_limit:
            return False
        
        # Increment count
        await conn.execute(
            "UPDATE rate_limits SET count = count + 1 WHERE id = $1",
            record["id"]
        )
        return True


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

async def init_db():
    """Initialize database tables"""
    async with pool.acquire() as conn:
        # Enable UUID extension
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        
        # Users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                google_id VARCHAR(255),
                picture TEXT,
                role VARCHAR(50) DEFAULT 'user',
                tier VARCHAR(50) DEFAULT 'free',
                subscription_status VARCHAR(50) DEFAULT 'inactive',
                stripe_customer_id VARCHAR(255),
                stripe_subscription_id VARCHAR(255),
                email_provider JSONB,
                email_provider_type VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Leads table with user_id
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                business_name VARCHAR(500) NOT NULL,
                owner_name VARCHAR(500),
                owner_email VARCHAR(255),
                owner_phone VARCHAR(50),
                industry VARCHAR(200),
                revenue INTEGER,
                employees INTEGER,
                city VARCHAR(200),
                state VARCHAR(100),
                description TEXT,
                status VARCHAR(50) DEFAULT 'new',
                pipeline_state VARCHAR(50) DEFAULT 'inbox',
                score DECIMAL(5, 2),
                source VARCHAR(100),
                source_url TEXT,
                approved_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # User actions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
                action VARCHAR(50) NOT NULL,
                reason TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Activities table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                type VARCHAR(100) NOT NULL,
                lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
                lead_name VARCHAR(500),
                description TEXT NOT NULL,
                metadata JSONB,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Outreach messages table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS outreach_messages (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
                lead_email VARCHAR(255),
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                message_type VARCHAR(50) DEFAULT 'email',
                status VARCHAR(50) DEFAULT 'pending',
                sent_at TIMESTAMP WITH TIME ZONE,
                opened_at TIMESTAMP WITH TIME ZONE,
                replied_at TIMESTAMP WITH TIME ZONE,
                provider VARCHAR(50),
                provider_message_id VARCHAR(255),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Bookings table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
                lead_email VARCHAR(255),
                lead_phone VARCHAR(50),
                booking_type VARCHAR(50) DEFAULT 'call',
                status VARCHAR(50) DEFAULT 'pending',
                scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
                duration_minutes INTEGER DEFAULT 30,
                notes TEXT,
                calendar_event_id VARCHAR(255),
                meeting_link TEXT,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Rate limits table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                resource_type VARCHAR(50) NOT NULL,
                count INTEGER DEFAULT 0,
                reset_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, resource_type)
            )
        """)
        
        # Create indexes for performance
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_user_id ON leads(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_user_status ON leads(user_id, status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_user_pipeline ON leads(user_id, pipeline_state)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_user_timestamp ON activities(user_id, timestamp DESC)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_outreach_user_id ON outreach_messages(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_outreach_user_status ON outreach_messages(user_id, status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_bookings_user_scheduled ON bookings(user_id, scheduled_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_rate_limits_user_resource ON rate_limits(user_id, resource_type)")
        
        # Create updated_at trigger function
        await conn.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)
        
        # Apply triggers
        for table in ['users', 'leads', 'outreach_messages', 'bookings', 'rate_limits']:
            await conn.execute(f"""
                DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};
                CREATE TRIGGER update_{table}_updated_at 
                BEFORE UPDATE ON {table} 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
            """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global pool, redis_client
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Initialize connection pool
    pool = await asyncpg.create_pool(
        DATABASE_URL, 
        min_size=5, 
        max_size=20,
        command_timeout=60,
        server_settings={
            'jit': 'off'
        }
    )
    
    # Initialize Redis
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Rate limiting will use database fallback.")
        redis_client = None
    
    await init_db()
    logger.info("Connected to database and initialized tables")
    
    yield
    
    await pool.close()
    if redis_client:
        await redis_client.close()
    logger.info("Shutdown complete")


# Create app
app = FastAPI(
    title="ACQUISITOR API",
    description="Autonomous acquisition platform - Multi-tenant secure edition",
    version="2.0.0",
    lifespan=lifespan
)

# CORS - configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        redis_status = "connected"
        if redis_client:
            try:
                await redis_client.ping()
            except:
                redis_status = "disconnected"
        else:
            redis_status = "not configured"
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": redis_status,
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/auth/google")
async def google_auth(auth_data: GoogleAuthRequest):
    """Handle Google OAuth authentication"""
    try:
        # Verify Google token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={auth_data.token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Google token")
            
            token_info = response.json()
            
            # Verify client ID
            if GOOGLE_CLIENT_ID and token_info.get("aud") != GOOGLE_CLIENT_ID:
                raise HTTPException(status_code=400, detail="Invalid client ID")
            
            # Verify email matches
            if token_info.get("email") != auth_data.email:
                raise HTTPException(status_code=400, detail="Email mismatch")
        
        async with pool.acquire() as conn:
            # Check if user exists
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                auth_data.email
            )
            
            if user:
                # Update user info
                await conn.execute(
                    """UPDATE users 
                       SET name = $1, picture = $2, updated_at = NOW()
                       WHERE id = $3""",
                    auth_data.name, auth_data.picture, user["id"]
                )
                user_id = user["id"]
                user_tier = user.get("tier", "free")
            else:
                # Create new user with free tier
                user_id = await conn.fetchval(
                    """INSERT INTO users (email, name, picture, google_id, tier)
                       VALUES ($1, $2, $3, $4, $5)
                       RETURNING id""",
                    auth_data.email, auth_data.name, auth_data.picture,
                    token_info.get("sub"), "free"
                )
                user_tier = "free"
        
        # Create JWT token
        access_token = create_access_token({
            "sub": str(user_id), 
            "email": auth_data.email,
            "tier": user_tier
        })
        
        return {
            "success": True,
            "token": access_token,
            "user": {
                "id": str(user_id),
                "email": auth_data.email,
                "name": auth_data.name,
                "picture": auth_data.picture,
                "tier": user_tier
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.get("/auth/me")
async def get_me(current_user: Dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": str(current_user["id"]),
        "email": current_user["email"],
        "name": current_user.get("name"),
        "role": current_user.get("role", "user"),
        "tier": current_user.get("tier", "free"),
        "created_at": current_user["created_at"]
    }


@app.post("/auth/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """Logout user (client should delete token)"""
    return {"success": True, "message": "Logged out successfully"}


# ============================================================================
# LEADS ENDPOINTS (SECURE - Multi-tenant)
# ============================================================================

@app.get("/leads")
async def list_leads(
    status: Optional[str] = None,
    pipeline_state: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """List all leads for the current user ONLY"""
    async with pool.acquire() as conn:
        query = "SELECT * FROM leads WHERE user_id = $1"
        params = [current_user["id"]]
        
        if status:
            query += f" AND status = ${len(params)+1}"
            params.append(status)
        
        if pipeline_state:
            query += f" AND pipeline_state = ${len(params)+1}"
            params.append(pipeline_state)
        
        query += " ORDER BY created_at DESC"
        
        rows = await conn.fetch(query, *params)
    
    return [dict(row) for row in rows]


@app.post("/leads")
@rate_limit(limit=50, per="day", tier_field="tier")
async def create_lead(
    lead: LeadCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new lead for the current user"""
    lead_id = uuid.uuid4()
    
    # Calculate initial score
    score = calculate_lead_score(lead)
    
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO leads 
               (id, user_id, business_name, owner_name, owner_email, owner_phone,
                industry, revenue, employees, city, state, description,
                source, score, status, pipeline_state)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)""",
            lead_id, current_user["id"], lead.business_name, lead.owner_name, lead.owner_email,
            lead.owner_phone, lead.industry, lead.revenue, lead.employees,
            lead.city, lead.state, lead.description, lead.source, score,
            "new", "inbox"
        )
        
        # Log activity
        await conn.execute(
            """INSERT INTO activities (type, lead_id, lead_name, description, user_id)
               VALUES ($1, $2, $3, $4, $5)""",
            "lead_created", lead_id, lead.business_name,
            f"Lead created: {lead.business_name}", current_user["id"]
        )
    
    return {
        "success": True,
        "id": str(lead_id),
        "score": score
    }


def calculate_lead_score(lead: LeadCreate) -> float:
    """Calculate lead score (0-100)"""
    score = 50.0  # Base score
    
    # Revenue score (0-30)
    if lead.revenue:
        if lead.revenue >= 5000000:
            score += 30
        elif lead.revenue >= 2000000:
            score += 20
        elif lead.revenue >= 1000000:
            score += 10
    
    # Employee score (0-10)
    if lead.employees:
        if lead.employees >= 20:
            score += 10
        elif lead.employees >= 10:
            score += 5
    
    # Industry bonus (0-10)
    good_industries = ['Technology', 'Healthcare', 'Services', 'Manufacturing', 'SaaS', 'Software']
    if lead.industry and any(ind in lead.industry for ind in good_industries):
        score += 10
    
    return min(100.0, score)


@app.get("/leads/{lead_id}")
async def get_lead(
    lead_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get a single lead - ONLY if owned by current user"""
    async with pool.acquire() as conn:
        lead = await conn.fetchrow(
            "SELECT * FROM leads WHERE id = $1 AND user_id = $2",
            uuid.UUID(lead_id), current_user["id"]
        )
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {"success": True, "data": dict(lead)}


@app.patch("/leads/{lead_id}")
async def update_lead(
    lead_id: str,
    update: LeadUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """Update a lead - ONLY if owned by current user"""
    async with pool.acquire() as conn:
        # Verify ownership
        lead = await conn.fetchrow(
            "SELECT * FROM leads WHERE id = $1 AND user_id = $2",
            uuid.UUID(lead_id), current_user["id"]
        )
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Build update query dynamically
        updates = []
        params = []
        
        if update.status is not None:
            updates.append(f"status = ${len(params)+1}")
            params.append(update.status)
        
        if update.pipeline_state is not None:
            updates.append(f"pipeline_state = ${len(params)+1}")
            params.append(update.pipeline_state)
        
        if update.score is not None:
            updates.append(f"score = ${len(params)+1}")
            params.append(update.score)
        
        if update.owner_name is not None:
            updates.append(f"owner_name = ${len(params)+1}")
            params.append(update.owner_name)
        
        if update.owner_email is not None:
            updates.append(f"owner_email = ${len(params)+1}")
            params.append(update.owner_email)
        
        if update.owner_phone is not None:
            updates.append(f"owner_phone = ${len(params)+1}")
            params.append(update.owner_phone)
        
        if updates:
            query = f"UPDATE leads SET {', '.join(updates)}, updated_at = NOW() WHERE id = ${len(params)+1} AND user_id = ${len(params)+2}"
            params.extend([uuid.UUID(lead_id), current_user["id"]])
            await conn.execute(query, *params)
            
            # Log activity
            await conn.execute(
                """INSERT INTO activities (type, lead_id, lead_name, description, user_id)
                   VALUES ($1, $2, $3, $4, $5)""",
                "lead_updated", uuid.UUID(lead_id), lead["business_name"],
                f"Lead updated: {lead['business_name']}", current_user["id"]
            )
    
    return {"success": True}


@app.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete a lead - ONLY if owned by current user"""
    async with pool.acquire() as conn:
        # Verify ownership and delete
        result = await conn.execute(
            "DELETE FROM leads WHERE id = $1 AND user_id = $2",
            uuid.UUID(lead_id), current_user["id"]
        )
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Log activity
        await conn.execute(
            """INSERT INTO activities (type, lead_id, description, user_id)
               VALUES ($1, $2, $3, $4)""",
            "lead_deleted", uuid.UUID(lead_id),
            f"Lead deleted: {lead_id}", current_user["id"]
        )
    
    return {"success": True, "message": "Lead deleted"}


# ============================================================================
# PIPELINE ENDPOINTS (SECURE - Multi-tenant)
# ============================================================================

@app.get("/pipeline")
async def get_pipeline(current_user: Dict = Depends(get_current_user)):
    """Get pipeline stages with leads - ONLY for current user"""
    stages = ["inbox", "qualified", "contacted", "meeting", "offer", "due_diligence", "closed"]
    
    async with pool.acquire() as conn:
        pipeline = {}
        for stage in stages:
            rows = await conn.fetch(
                """SELECT * FROM leads 
                   WHERE user_id = $1 AND pipeline_state = $2 AND status = 'active'
                   ORDER BY score DESC NULLS LAST""",
                current_user["id"], stage
            )
            pipeline[stage] = [dict(row) for row in rows]
    
    return {
        "success": True,
        "data": pipeline
    }


# ============================================================================
# ACTIVITY ENDPOINTS (SECURE - Multi-tenant)
# ============================================================================

@app.get("/activities")
async def get_activities(
    limit: int = 20,
    current_user: Dict = Depends(get_current_user)
):
    """Get recent activities - ONLY for current user"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM activities 
               WHERE user_id = $1
               ORDER BY timestamp DESC LIMIT $2""",
            current_user["id"], limit
        )
    
    return {
        "success": True,
        "data": [dict(row) for row in rows]
    }


# ============================================================================
# OUTREACH ENDPOINTS (SECURE - Multi-tenant)
# ============================================================================

@app.get("/outreach")
async def list_outreach(
    status: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """List all outreach messages for current user"""
    async with pool.acquire() as conn:
        query = "SELECT * FROM outreach_messages WHERE user_id = $1"
        params = [current_user["id"]]
        
        if status:
            query += f" AND status = ${len(params)+1}"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        rows = await conn.fetch(query, *params)
    
    return {"success": True, "data": [dict(row) for row in rows]}


@app.post("/outreach")
@rate_limit(limit=25, per="day", tier_field="tier")
async def create_outreach(
    outreach: OutreachCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create outreach message for a lead"""
    async with pool.acquire() as conn:
        # Verify lead ownership
        lead = await conn.fetchrow(
            "SELECT * FROM leads WHERE id = $1 AND user_id = $2",
            uuid.UUID(outreach.lead_id), current_user["id"]
        )
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Create outreach message
        message_id = uuid.uuid4()
        await conn.execute(
            """INSERT INTO outreach_messages 
               (id, user_id, lead_id, lead_email, subject, body, message_type, status)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            message_id, current_user["id"], uuid.UUID(outreach.lead_id),
            lead.get("owner_email"), outreach.subject, outreach.body,
            outreach.message_type, "pending"
        )
        
        # Log activity
        await conn.execute(
            """INSERT INTO activities (type, lead_id, lead_name, description, user_id)
               VALUES ($1, $2, $3, $4, $5)""",
            "outreach_created", uuid.UUID(outreach.lead_id), lead["business_name"],
            f"Outreach created for: {lead['business_name']}", current_user["id"]
        )
    
    return {
        "success": True,
        "id": str(message_id),
        "status": "pending"
    }


@app.get("/outreach/{message_id}")
async def get_outreach(
    message_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get a single outreach message - ONLY if owned by current user"""
    async with pool.acquire() as conn:
        message = await conn.fetchrow(
            "SELECT * FROM outreach_messages WHERE id = $1 AND user_id = $2",
            uuid.UUID(message_id), current_user["id"]
        )
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"success": True, "data": dict(message)}


# ============================================================================
# EMAIL PROVIDER ENDPOINTS (Multi-tenant)
# ============================================================================

@app.get("/email/provider")
async def get_email_provider(current_user: Dict = Depends(get_current_user)):
    """Get current user's email provider configuration (without credentials)"""
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT email_provider_type, email_provider FROM users WHERE id = $1",
            current_user["id"]
        )
    
    if not user or not user["email_provider_type"]:
        return {"success": True, "configured": False}
    
    # Return only provider type and non-sensitive metadata
    provider = user["email_provider"] or {}
    return {
        "success": True,
        "configured": True,
        "provider_type": user["email_provider_type"],
        "sender_email": provider.get("sender_email")
    }


@app.post("/email/provider")
async def setup_email_provider(
    setup: EmailProviderSetup,
    current_user: Dict = Depends(get_current_user)
):
    """Setup email provider for current user"""
    # Validate provider type
    valid_providers = ["gmail", "sendgrid", "outlook"]
    if setup.provider_type not in valid_providers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid provider type. Must be one of: {', '.join(valid_providers)}"
        )
    
    # Encrypt/store credentials (in production, use proper encryption)
    async with pool.acquire() as conn:
        await conn.execute(
            """UPDATE users 
               SET email_provider_type = $1,
                   email_provider = $2,
                   updated_at = NOW()
               WHERE id = $3""",
            setup.provider_type,
            json.dumps(setup.credentials),
            current_user["id"]
        )
    
    return {
        "success": True,
        "message": f"Email provider '{setup.provider_type}' configured successfully"
    }


@app.delete("/email/provider")
async def remove_email_provider(current_user: Dict = Depends(get_current_user)):
    """Remove email provider configuration"""
    async with pool.acquire() as conn:
        await conn.execute(
            """UPDATE users 
               SET email_provider_type = NULL,
                   email_provider = NULL,
                   updated_at = NOW()
               WHERE id = $1""",
            current_user["id"]
        )
    
    return {"success": True, "message": "Email provider removed"}


# ============================================================================
# USER SETTINGS & RATE LIMITS
# ============================================================================

@app.get("/user/limits")
async def get_user_limits(current_user: Dict = Depends(get_current_user)):
    """Get current user's rate limit status"""
    tier = current_user.get("tier", "free")
    tier_limits = TIER_LIMITS.get(tier, FREE_TIER)
    
    # Get current usage from Redis or DB
    usage = {}
    today = datetime.utcnow().strftime('%Y%m%d')
    
    for resource_type in ["leads", "emails", "scrapes"]:
        if redis_client:
            rate_key = f"rate_limit:{current_user['id']}:{resource_type}:{today}"
            count = await redis_client.get(rate_key) or 0
        else:
            # Fallback to DB
            async with pool.acquire() as conn:
                record = await conn.fetchrow(
                    """SELECT count FROM rate_limits 
                       WHERE user_id = $1 AND resource_type = $2""",
                    current_user["id"], resource_type
                )
                count = record["count"] if record else 0
        
        limit = tier_limits.get(resource_type, 0)
        usage[resource_type] = {
            "used": int(count),
            "limit": limit if limit != float('inf') else None,
            "remaining": None if limit == float('inf') else max(0, limit - int(count))
        }
    
    return {
        "success": True,
        "tier": tier,
        "limits": usage
    }


# ============================================================================
# LEGACY API COMPATIBILITY (SECURE - Multi-tenant)
# ============================================================================

@app.get("/api/scout/leads")
async def legacy_get_leads(
    status: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Legacy endpoint for leads - SECURE"""
    leads = await list_leads(status=status, current_user=current_user)
    return {"success": True, "data": leads, "meta": {"total": len(leads)}}


@app.post("/api/scout/leads")
async def legacy_create_lead(
    lead: LeadCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Legacy endpoint for creating leads - SECURE"""
    result = await create_lead(lead=lead, current_user=current_user)
    return result


@app.get("/api/pipeline")
async def legacy_get_pipeline(current_user: Dict = Depends(get_current_user)):
    """Legacy endpoint for pipeline - SECURE"""
    result = await get_pipeline(current_user=current_user)
    return result


@app.get("/api/activity")
async def legacy_get_activities(
    limit: int = 20,
    current_user: Dict = Depends(get_current_user)
):
    """Legacy endpoint for activities - SECURE"""
    result = await get_activities(limit=limit, current_user=current_user)
    return result


@app.get("/api/metrics")
async def get_metrics(current_user: Dict = Depends(get_current_user)):
    """Get dashboard metrics - SECURE (user-scoped)"""
    async with pool.acquire() as conn:
        # Total leads for this user
        total_leads = await conn.fetchval(
            "SELECT COUNT(*) FROM leads WHERE user_id = $1",
            current_user["id"]
        )
        
        # Pipeline leads for this user
        pipeline_leads = await conn.fetchval(
            """SELECT COUNT(*) FROM leads 
               WHERE user_id = $1 AND status = 'active' AND pipeline_state != 'inbox'""",
            current_user["id"]
        )
        
        # New leads this week for this user
        new_leads = await conn.fetchval(
            """SELECT COUNT(*) FROM leads 
               WHERE user_id = $1 AND created_at > NOW() - INTERVAL '7 days'""",
            current_user["id"]
        )
        
        # Average score for this user's leads
        avg_score = await conn.fetchval(
            """SELECT AVG(score) FROM leads 
               WHERE user_id = $1 AND score IS NOT NULL""",
            current_user["id"]
        )
        
        # Emails sent by this user
        emails_sent = await conn.fetchval(
            """SELECT COUNT(*) FROM outreach_messages 
               WHERE user_id = $1 AND status = 'sent'""",
            current_user["id"]
        )
        
        # Calls booked by this user
        calls_booked = await conn.fetchval(
            """SELECT COUNT(*) FROM bookings 
               WHERE user_id = $1""",
            current_user["id"]
        )
    
    return {
        "success": True,
        "data": {
            "totalLeads": total_leads or 0,
            "leadsInPipeline": pipeline_leads or 0,
            "newLeadsThisWeek": new_leads or 0,
            "averageScore": round(avg_score, 1) if avg_score else 0,
            "emailsSent": emails_sent or 0,
            "emailsOpened": 0,
            "emailsReplied": 0,
            "openRate": 0,
            "replyRate": 0,
            "callsBooked": calls_booked or 0,
            "averageDealSize": 0
        }
    }


# ============================================================================
# BILLING ENDPOINTS
# ============================================================================

@app.get("/billing/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return {
        "success": True,
        "data": {
            "publishable_key": STRIPE_PUBLISHABLE_KEY,
            "pro_price_id": STRIPE_PRO_PRICE_ID,
            "enterprise_price_id": STRIPE_ENTERPRISE_PRICE_ID
        }
    }


@app.post("/billing/checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Create a Stripe checkout session for subscription"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    # Get price ID based on tier
    price_id = STRIPE_PRO_PRICE_ID if request.tier == "pro" else STRIPE_ENTERPRISE_PRICE_ID
    if not price_id:
        raise HTTPException(status_code=400, detail=f"Price ID not configured for tier: {request.tier}")
    
    try:
        # Get or create Stripe customer
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT stripe_customer_id FROM users WHERE id = $1",
                current_user["id"]
            )
            
            stripe_customer_id = user.get("stripe_customer_id")
            
            # Create customer if doesn't exist
            if not stripe_customer_id:
                customer = stripe.Customer.create(
                    email=current_user["email"],
                    name=current_user.get("name", ""),
                    metadata={"user_id": str(current_user["id"])}
                )
                stripe_customer_id = customer.id
                
                # Save customer ID to database
                await conn.execute(
                    "UPDATE users SET stripe_customer_id = $1 WHERE id = $2",
                    stripe_customer_id, current_user["id"]
                )
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                "user_id": str(current_user["id"]),
                "tier": request.tier
            }
        )
        
        return {
            "success": True,
            "data": {
                "session_id": checkout_session.id,
                "url": checkout_session.url
            }
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/billing/subscription")
async def get_subscription(current_user: Dict = Depends(get_current_user)):
    """Get current user's subscription status"""
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            """SELECT tier, subscription_status, stripe_subscription_id 
               FROM users WHERE id = $1""",
            current_user["id"]
        )
    
    subscription_data = {
        "tier": user["tier"] or "free",
        "status": user["subscription_status"] or "inactive",
        "current_period_end": None,
        "cancel_at_period_end": False
    }
    
    # If there's a Stripe subscription, get latest details
    if user.get("stripe_subscription_id") and STRIPE_SECRET_KEY:
        try:
            sub = stripe.Subscription.retrieve(user["stripe_subscription_id"])
            subscription_data["current_period_end"] = datetime.fromtimestamp(sub.current_period_end)
            subscription_data["cancel_at_period_end"] = sub.cancel_at_period_end
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription: {e}")
    
    return {"success": True, "data": subscription_data}


@app.post("/billing/portal")
async def create_portal_session(current_user: Dict = Depends(get_current_user)):
    """Create Stripe customer portal session"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT stripe_customer_id FROM users WHERE id = $1",
            current_user["id"]
        )
    
    if not user.get("stripe_customer_id"):
        raise HTTPException(status_code=400, detail="No Stripe customer found")
    
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user["stripe_customer_id"],
            return_url=f"{FRONTEND_URL}/dashboard/settings"
        )
        
        return {"success": True, "data": {"url": portal_session.url}}
    except stripe.error.StripeError as e:
        logger.error(f"Stripe portal error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/billing/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not STRIPE_WEBHOOK_SECRET:
        logger.warning("Stripe webhook secret not configured")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    event_type = event["type"]
    data = event["data"]["object"]
    
    logger.info(f"Processing Stripe webhook: {event_type}")
    
    if event_type == "checkout.session.completed":
        await handle_checkout_completed(data)
    elif event_type == "invoice.paid":
        await handle_invoice_paid(data)
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(data)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(data)
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data)
    
    return {"success": True}


async def handle_checkout_completed(session: dict):
    """Handle checkout.session.completed"""
    user_id = session.get("metadata", {}).get("user_id")
    tier = session.get("metadata", {}).get("tier", "pro")
    subscription_id = session.get("subscription")
    
    if not user_id:
        logger.error("No user_id in checkout session metadata")
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """UPDATE users 
                   SET tier = $1, 
                       subscription_status = 'active',
                       stripe_subscription_id = $2,
                       updated_at = NOW()
                   WHERE id = $3""",
                tier, subscription_id, uuid.UUID(user_id)
            )
        logger.info(f"Activated subscription for user {user_id}: {tier}")
    except Exception as e:
        logger.error(f"Error activating subscription: {e}")


async def handle_invoice_paid(invoice: dict):
    """Handle invoice.paid"""
    subscription_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    
    if not subscription_id:
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """UPDATE users 
                   SET subscription_status = 'active',
                       updated_at = NOW()
                   WHERE stripe_subscription_id = $1""",
                subscription_id
            )
        logger.info(f"Subscription paid: {subscription_id}")
    except Exception as e:
        logger.error(f"Error updating paid invoice: {e}")


async def handle_payment_failed(invoice: dict):
    """Handle invoice.payment_failed"""
    subscription_id = invoice.get("subscription")
    
    if not subscription_id:
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """UPDATE users 
                   SET subscription_status = 'past_due',
                       updated_at = NOW()
                   WHERE stripe_subscription_id = $1""",
                subscription_id
            )
        logger.info(f"Subscription payment failed: {subscription_id}")
    except Exception as e:
        logger.error(f"Error updating failed payment: {e}")


async def handle_subscription_deleted(subscription: dict):
    """Handle customer.subscription.deleted"""
    subscription_id = subscription.get("id")
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """UPDATE users 
                   SET tier = 'free',
                       subscription_status = 'inactive',
                       stripe_subscription_id = NULL,
                       updated_at = NOW()
                   WHERE stripe_subscription_id = $1""",
                subscription_id
            )
        logger.info(f"Subscription deleted, downgraded to free: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling subscription deletion: {e}")


async def handle_subscription_updated(subscription: dict):
    """Handle customer.subscription.updated"""
    subscription_id = subscription.get("id")
    status = subscription.get("status")
    
    # Map Stripe status to our status
    status_map = {
        "active": "active",
        "canceled": "canceled",
        "incomplete": "inactive",
        "incomplete_expired": "inactive",
        "past_due": "past_due",
        "paused": "paused",
        "trialing": "active",
        "unpaid": "past_due"
    }
    
    our_status = status_map.get(status, "inactive")
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """UPDATE users 
                   SET subscription_status = $1,
                       updated_at = NOW()
                   WHERE stripe_subscription_id = $2""",
                our_status, subscription_id
            )
        logger.info(f"Subscription updated: {subscription_id} -> {our_status}")
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
