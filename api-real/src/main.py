# ACQUISITOR Production API
# FastAPI backend with PostgreSQL and Google OAuth

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import os
import uuid
import json
import asyncpg
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Global connection pool
pool: asyncpg.Pool = None

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


# Pydantic models
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


# Auth functions
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


async def init_db():
    """Initialize database tables"""
    async with pool.acquire() as conn:
        # Users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                google_id VARCHAR(255),
                picture TEXT,
                role VARCHAR(50) DEFAULT 'user',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Leads table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
                type VARCHAR(100) NOT NULL,
                lead_id UUID REFERENCES leads(id),
                lead_name VARCHAR(500),
                description TEXT NOT NULL,
                user_id UUID REFERENCES users(id),
                metadata JSONB,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
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
        
        # Apply trigger to users
        await conn.execute("""
            DROP TRIGGER IF EXISTS update_users_updated_at ON users;
            CREATE TRIGGER update_users_updated_at 
            BEFORE UPDATE ON users 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)
        
        # Apply trigger to leads
        await conn.execute("""
            DROP TRIGGER IF EXISTS update_leads_updated_at ON leads;
            CREATE TRIGGER update_leads_updated_at 
            BEFORE UPDATE ON leads 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global pool
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    await init_db()
    print("Connected to database")
    yield
    await pool.close()


# Create app
app = FastAPI(
    title="ACQUISITOR API",
    description="Autonomous acquisition platform",
    version="1.0.0",
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
        return {
            "status": "healthy",
            "database": "connected",
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
            else:
                # Create new user
                user_id = await conn.fetchval(
                    """INSERT INTO users (email, name, picture, google_id)
                       VALUES ($1, $2, $3, $4)
                       RETURNING id""",
                    auth_data.email, auth_data.name, auth_data.picture,
                    token_info.get("sub")
                )
        
        # Create JWT token
        access_token = create_access_token({"sub": str(user_id), "email": auth_data.email})
        
        return {
            "success": True,
            "token": access_token,
            "user": {
                "id": str(user_id),
                "email": auth_data.email,
                "name": auth_data.name,
                "picture": auth_data.picture
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.get("/auth/me")
async def get_me(current_user: Dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": str(current_user["id"]),
        "email": current_user["email"],
        "name": current_user.get("name"),
        "role": current_user.get("role", "user"),
        "created_at": current_user["created_at"]
    }


@app.post("/auth/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """Logout user (client should delete token)"""
    return {"success": True, "message": "Logged out successfully"}


# ============================================================================
# LEADS ENDPOINTS
# ============================================================================

@app.get("/leads")
async def list_leads(
    status: Optional[str] = None,
    pipeline_state: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """List all leads for the current user"""
    async with pool.acquire() as conn:
        query = "SELECT * FROM leads"
        params = []
        conditions = []
        
        if status:
            conditions.append(f"status = ${len(params)+1}")
            params.append(status)
        
        if pipeline_state:
            conditions.append(f"pipeline_state = ${len(params)+1}")
            params.append(pipeline_state)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        rows = await conn.fetch(query, *params)
    
    return [dict(row) for row in rows]


@app.post("/leads")
async def create_lead(
    lead: LeadCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new lead"""
    lead_id = uuid.uuid4()
    
    # Calculate initial score
    score = calculate_lead_score(lead)
    
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO leads 
               (id, business_name, owner_name, owner_email, owner_phone,
                industry, revenue, employees, city, state, description,
                source, score, status, pipeline_state)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)""",
            lead_id, lead.business_name, lead.owner_name, lead.owner_email,
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
    """Get a single lead"""
    async with pool.acquire() as conn:
        lead = await conn.fetchrow(
            "SELECT * FROM leads WHERE id = $1",
            uuid.UUID(lead_id)
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
    """Update a lead"""
    async with pool.acquire() as conn:
        lead = await conn.fetchrow(
            "SELECT * FROM leads WHERE id = $1",
            uuid.UUID(lead_id)
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
            query = f"UPDATE leads SET {', '.join(updates)}, updated_at = NOW() WHERE id = ${len(params)+1}"
            params.append(uuid.UUID(lead_id))
            await conn.execute(query, *params)
            
            # Log activity
            await conn.execute(
                """INSERT INTO activities (type, lead_id, lead_name, description, user_id)
                   VALUES ($1, $2, $3, $4, $5)""",
                "lead_updated", uuid.UUID(lead_id), lead["business_name"],
                f"Lead updated: {lead['business_name']}", current_user["id"]
            )
    
    return {"success": True}


# ============================================================================
# PIPELINE ENDPOINTS
# ============================================================================

@app.get("/pipeline")
async def get_pipeline(current_user: Dict = Depends(get_current_user)):
    """Get pipeline stages with leads"""
    stages = ["inbox", "qualified", "contacted", "meeting", "offer", "due_diligence", "closed"]
    
    async with pool.acquire() as conn:
        pipeline = {}
        for stage in stages:
            rows = await conn.fetch(
                """SELECT * FROM leads 
                   WHERE pipeline_state = $1 AND status = 'active'
                   ORDER BY score DESC NULLS LAST""",
                stage
            )
            pipeline[stage] = [dict(row) for row in rows]
    
    return {
        "success": True,
        "data": pipeline
    }


# ============================================================================
# ACTIVITY ENDPOINTS
# ============================================================================

@app.get("/activities")
async def get_activities(
    limit: int = 20,
    current_user: Dict = Depends(get_current_user)
):
    """Get recent activities"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM activities 
               ORDER BY timestamp DESC LIMIT $1""",
            limit
        )
    
    return {
        "success": True,
        "data": [dict(row) for row in rows]
    }


# ============================================================================
# LEGACY API COMPATIBILITY (for existing frontend)
# ============================================================================

@app.get("/api/scout/leads")
async def legacy_get_leads(
    status: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Legacy endpoint for leads"""
    leads = await list_leads(status=status, current_user=current_user)
    return {"success": True, "data": leads, "meta": {"total": len(leads)}}


@app.post("/api/scout/leads")
async def legacy_create_lead(
    lead: LeadCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Legacy endpoint for creating leads"""
    result = await create_lead(lead, current_user)
    return result


@app.get("/api/pipeline")
async def legacy_get_pipeline(current_user: Dict = Depends(get_current_user)):
    """Legacy endpoint for pipeline"""
    result = await get_pipeline(current_user)
    return result


@app.get("/api/activity")
async def legacy_get_activities(
    limit: int = 20,
    current_user: Dict = Depends(get_current_user)
):
    """Legacy endpoint for activities"""
    result = await get_activities(limit, current_user)
    return result


@app.get("/api/metrics")
async def get_metrics(current_user: Dict = Depends(get_current_user)):
    """Get dashboard metrics"""
    async with pool.acquire() as conn:
        total_leads = await conn.fetchval("SELECT COUNT(*) FROM leads")
        
        pipeline_leads = await conn.fetchval(
            """SELECT COUNT(*) FROM leads 
               WHERE status = 'active' AND pipeline_state != 'inbox'"""
        )
        
        new_leads = await conn.fetchval(
            """SELECT COUNT(*) FROM leads 
               WHERE created_at > NOW() - INTERVAL '7 days'"""
        )
        
        avg_score = await conn.fetchval(
            """SELECT AVG(score) FROM leads WHERE score IS NOT NULL"""
        )
    
    return {
        "success": True,
        "data": {
            "totalLeads": total_leads or 0,
            "leadsInPipeline": pipeline_leads or 0,
            "newLeadsThisWeek": new_leads or 0,
            "averageScore": round(avg_score, 1) if avg_score else 0,
            "emailsSent": 0,
            "emailsOpened": 0,
            "emailsReplied": 0,
            "openRate": 0,
            "replyRate": 0,
            "callsBooked": 0,
            "averageDealSize": 0
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
