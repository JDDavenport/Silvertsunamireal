# ACQUISITOR Real Backend
# Production API with PostgreSQL

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import uuid
import asyncpg
from contextlib import asynccontextmanager

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/acquisitor")

# Global connection pool
pool: asyncpg.Pool = None

async def init_db():
    """Initialize database tables"""
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS buyer_profiles (
                id TEXT PRIMARY KEY,
                background TEXT,
                industries TEXT[],
                acquisition_experience TEXT,
                motivation TEXT,
                values TEXT[],
                location_preference TEXT[],
                budget_min INTEGER,
                budget_max INTEGER,
                revenue_min INTEGER,
                revenue_max INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT,
                score INTEGER DEFAULT 0,
                revenue INTEGER,
                employees INTEGER,
                city TEXT,
                state TEXT,
                description TEXT,
                status TEXT DEFAULT 'new',
                email TEXT,
                phone TEXT,
                source TEXT,
                ai_assessment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contact TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                lead_id TEXT,
                lead_name TEXT,
                description TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS email_threads (
                id TEXT PRIMARY KEY,
                lead_id TEXT,
                gmail_thread_id TEXT,
                sequence_step INTEGER DEFAULT 0,
                last_message_at TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id SERIAL PRIMARY KEY,
                date DATE DEFAULT CURRENT_DATE,
                emails_sent INTEGER DEFAULT 0,
                emails_opened INTEGER DEFAULT 0,
                emails_replied INTEGER DEFAULT 0,
                calls_booked INTEGER DEFAULT 0
            )
        """)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    await init_db()
    print(f"✅ Connected to database")
    yield
    await pool.close()

app = FastAPI(
    title="ACQUISITOR API",
    description="Autonomous acquisition platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class BuyerProfileCreate(BaseModel):
    background: str
    industries: List[str]
    acquisition_experience: str
    motivation: str
    values: List[str]
    location_preference: List[str]
    budget_min: int
    budget_max: int
    revenue_min: int
    revenue_max: int

class LeadCreate(BaseModel):
    name: str
    industry: str
    revenue: int
    employees: int
    city: str
    state: str
    description: str
    source: str
    email: Optional[str] = None
    phone: Optional[str] = None

class LeadUpdate(BaseModel):
    status: str
    score: Optional[int] = None

class ActivityCreate(BaseModel):
    type: str
    lead_id: Optional[str] = None
    lead_name: Optional[str] = None
    description: str
    metadata: Optional[Dict[str, Any]] = None

# Health check
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

# Buyer Profile endpoints
@app.post("/api/intake/profile")
async def create_profile(profile: BuyerProfileCreate):
    """Create buyer profile"""
    profile_id = str(uuid.uuid4())
    
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO buyer_profiles 
            (id, background, industries, acquisition_experience, motivation, values,
             location_preference, budget_min, budget_max, revenue_min, revenue_max)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """, profile_id, profile.background, profile.industries,
            profile.acquisition_experience, profile.motivation, profile.values,
            profile.location_preference, profile.budget_min, profile.budget_max,
            profile.revenue_min, profile.revenue_max)
    
    return {"success": True, "id": profile_id}

@app.get("/api/intake/profile")
async def get_profile():
    """Get latest buyer profile"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM buyer_profiles 
            ORDER BY created_at DESC LIMIT 1
        """)
    
    if not row:
        raise HTTPException(status_code=404, detail="No profile found")
    
    return dict(row)

# Lead endpoints
@app.get("/api/scout/leads")
async def get_leads(status: Optional[str] = None):
    """Get all leads, optionally filtered by status"""
    async with pool.acquire() as conn:
        if status:
            rows = await conn.fetch("SELECT * FROM leads WHERE status = $1 ORDER BY score DESC", status)
        else:
            rows = await conn.fetch("SELECT * FROM leads ORDER BY score DESC")
    
    return {
        "success": True,
        "data": [dict(row) for row in rows],
        "meta": {"total": len(rows)}
    }

@app.get("/api/scout/leads/{lead_id}")
async def get_lead(lead_id: str):
    """Get single lead"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM leads WHERE id = $1", lead_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {"success": True, "data": dict(row)}

@app.post("/api/scout/leads")
async def create_lead(lead: LeadCreate):
    """Create new lead"""
    lead_id = str(uuid.uuid4())
    
    # Calculate score based on criteria
    score = calculate_score(lead)
    
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO leads 
            (id, name, industry, score, revenue, employees, city, state, 
             description, source, email, phone, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 'new')
        """, lead_id, lead.name, lead.industry, score, lead.revenue,
            lead.employees, lead.city, lead.state, lead.description,
            lead.source, lead.email, lead.phone)
    
    # Log activity
    await log_activity("lead_discovered", lead_id, lead.name, 
                       f"New lead discovered: {lead.name}")
    
    return {"success": True, "id": lead_id, "score": score}

@app.patch("/api/scout/leads/{lead_id}/status")
async def update_lead_status(lead_id: str, update: LeadUpdate):
    """Update lead status"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM leads WHERE id = $1", lead_id)
        if not row:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        await conn.execute(
            "UPDATE leads SET status = $1, score = COALESCE($2, score) WHERE id = $3",
            update.status, update.score, lead_id
        )
        
        lead_name = row['name']
    
    # Log activity
    await log_activity(f"lead_{update.status}", lead_id, lead_name,
                       f"Lead {update.status}: {lead_name}")
    
    return {"success": True}

# Pipeline endpoints
@app.get("/api/pipeline")
async def get_pipeline():
    """Get pipeline leads"""
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM leads 
            WHERE status IN ('approved', 'outreach', 'engaged', 'qualified', 'booked')
            ORDER BY score DESC
        """)
    
    return {
        "success": True,
        "data": [dict(row) for row in rows]
    }

# Activity endpoints
@app.get("/api/activity")
async def get_activities(limit: int = 20):
    """Get recent activities"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM activities ORDER BY timestamp DESC LIMIT $1",
            limit
        )
    
    return {
        "success": True,
        "data": [dict(row) for row in rows]
    }

async def log_activity(type_: str, lead_id: Optional[str], lead_name: Optional[str], 
                       description: str, metadata: Optional[Dict] = None):
    """Log an activity"""
    activity_id = str(uuid.uuid4())
    
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO activities (id, type, lead_id, lead_name, description, metadata)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, activity_id, type_, lead_id, lead_name, description, 
            json.dumps(metadata) if metadata else None)

# Metrics endpoints
@app.get("/api/metrics")
async def get_metrics():
    """Get dashboard metrics"""
    async with pool.acquire() as conn:
        # Get cumulative metrics
        metrics = await conn.fetchrow("""
            SELECT 
                COALESCE(SUM(emails_sent), 0) as emails_sent,
                COALESCE(SUM(emails_opened), 0) as emails_opened,
                COALESCE(SUM(emails_replied), 0) as emails_replied,
                COALESCE(SUM(calls_booked), 0) as calls_booked
            FROM metrics
        """)
        
        total_leads = await conn.fetchval("SELECT COUNT(*) FROM leads")
        pipeline_leads = await conn.fetchval("""
            SELECT COUNT(*) FROM leads 
            WHERE status IN ('approved', 'outreach', 'engaged', 'qualified', 'booked')
        """)
    
    emails_sent = metrics['emails_sent'] or 0
    emails_opened = metrics['emails_opened'] or 0
    emails_replied = metrics['emails_replied'] or 0
    
    open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0
    reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0
    
    return {
        "success": True,
        "data": {
            "totalLeads": total_leads,
            "leadsInPipeline": pipeline_leads,
            "emailsSent": emails_sent,
            "emailsOpened": emails_opened,
            "emailsReplied": emails_replied,
            "openRate": round(open_rate, 1),
            "replyRate": round(reply_rate, 1),
            "callsBooked": metrics['calls_booked'] or 0,
            "averageDealSize": 5200000  # Calculate from actual data
        }
    }

# Helper functions
def calculate_score(lead: LeadCreate) -> int:
    """Calculate lead score (0-100)"""
    score = 50  # Base score
    
    # Revenue score (0-30)
    if lead.revenue >= 5000000:
        score += 30
    elif lead.revenue >= 2000000:
        score += 20
    elif lead.revenue >= 1000000:
        score += 10
    
    # Employee score (0-10)
    if lead.employees >= 20:
        score += 10
    elif lead.employees >= 10:
        score += 5
    
    # Industry bonus (0-10)
    good_industries = ['Technology', 'Healthcare', 'Services', 'Manufacturing']
    if lead.industry in good_industries:
        score += 10
    
    return min(100, score)

# Discovery endpoint (triggered by cron)
@app.post("/api/scout/discover")
async def trigger_discovery(background_tasks: BackgroundTasks):
    """Trigger lead discovery (called by cron)"""
    background_tasks.add_task(discover_leads_task)
    return {"success": True, "message": "Discovery started"}

async def discover_leads_task():
    """Background task for lead discovery"""
    # TODO: Implement actual scraper calls
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
