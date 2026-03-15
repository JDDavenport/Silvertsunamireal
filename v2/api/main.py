from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import sqlite3
import json
import os
import asyncio
from pathlib import Path
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

# Database
DB_PATH = Path(__file__).parent / "acquisitor.db"

# JWT Config
SECRET_KEY = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# OAuth Config (for Gmail)
GOOGLE_CLIENT_ID = "238142947257-25pcmqi9vuamd1ntaoihbj8n9v7skt3s.apps.googleusercontent.com"

app = FastAPI(title="ACQUISITOR API v2", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    name: str

class User(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool = True

class BuyerProfile(BaseModel):
    background: str
    industries: List[str]
    budget_min: int
    budget_max: int
    revenue_min: int
    revenue_max: int
    location_preference: List[str]
    values: List[str]
    timeline: str = "flexible"
    criteria: Optional[Dict] = None

class Lead(BaseModel):
    id: str
    name: str
    industry: str
    revenue: int
    employees: int
    city: str
    state: str
    description: str
    score: int = 0
    status: str = "new"
    email: Optional[str] = None
    source: str = "unknown"

class AgentConfig(BaseModel):
    daily_email_limit: int = Field(default=10, ge=1, le=25)
    send_window_start: str = "09:00"
    send_window_end: str = "17:00"
    discovery_frequency: str = "daily"  # daily, every_2_days, weekly
    auto_approve_threshold: int = Field(default=0, ge=0, le=100)  # 0 = off
    reply_handling: str = "manual"  # manual, semi_auto, auto
    email_signature: str = "Best regards,\nJD"

# Database Functions
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            agent_config TEXT DEFAULT '{}'
        )
    """)
    
    # Buyer Profiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buyer_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id),
            background TEXT,
            industries TEXT,
            budget_min INTEGER,
            budget_max INTEGER,
            revenue_min INTEGER,
            revenue_max INTEGER,
            location_preference TEXT,
            values TEXT,
            timeline TEXT,
            criteria TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Leads (per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id),
            name TEXT,
            industry TEXT,
            revenue INTEGER,
            employees INTEGER,
            city TEXT,
            state TEXT,
            description TEXT,
            source TEXT,
            source_url TEXT,
            score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            email TEXT,
            phone TEXT,
            ai_assessment TEXT,
            email_sent INTEGER DEFAULT 0,
            email_sent_at TIMESTAMP,
            reply_received INTEGER DEFAULT 0,
            reply_classification TEXT,
            call_booked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity_at TIMESTAMP
        )
    """)
    
    # Agent Activities
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT REFERENCES users(id),
            type TEXT,
            lead_id TEXT,
            description TEXT,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Email Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT REFERENCES users(id),
            lead_id TEXT,
            to_email TEXT,
            subject TEXT,
            body TEXT,
            sent_at TIMESTAMP,
            sequence_step INTEGER DEFAULT 0
        )
    """)
    
    # Lead Notes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_notes (
            id TEXT PRIMARY KEY,
            lead_id TEXT REFERENCES leads(id),
            content TEXT,
            type TEXT DEFAULT 'note',
            created_by TEXT REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Lead Activities
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_activities (
            id TEXT PRIMARY KEY,
            lead_id TEXT REFERENCES leads(id),
            user_id TEXT REFERENCES users(id),
            type TEXT,
            description TEXT,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

# JWT Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Dependencies
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    
    return dict(row)

# Routes
@app.on_event("startup")
async def startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/auth/google")
async def auth_google(token: dict):
    """Verify Google ID token and create/login user"""
    # In production, verify with Google
    # For now, accept email and create user
    email = token.get("email")
    name = token.get("name", email.split("@")[0])
    
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    
    if row:
        # Update last login
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", 
                      (datetime.now().isoformat(), row["id"]))
        conn.commit()
        user_id = row["id"]
        is_new = False
    else:
        # Create new user
        user_id = secrets.token_urlsafe(16)
        cursor.execute("""
            INSERT INTO users (id, email, name, last_login)
            VALUES (?, ?, ?, ?)
        """, (user_id, email, name, datetime.now().isoformat()))
        conn.commit()
        is_new = True
    
    conn.close()
    
    # Create JWT
    access_token = create_access_token({"sub": user_id, "email": email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
        "email": email,
        "name": name,
        "is_new": is_new
    }

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "is_active": current_user["is_active"]
    }

@app.post("/onboarding/profile")
async def save_profile(profile: BuyerProfile, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if profile exists
    cursor.execute("SELECT id FROM buyer_profiles WHERE user_id = ?", (current_user["id"],))
    existing = cursor.fetchone()
    
    profile_id = existing["id"] if existing else secrets.token_urlsafe(16)
    
    if existing:
        cursor.execute("""
            UPDATE buyer_profiles SET
                background = ?, industries = ?, budget_min = ?, budget_max = ?,
                revenue_min = ?, revenue_max = ?, location_preference = ?,
                values = ?, timeline = ?, criteria = ?
            WHERE id = ?
        """, (
            profile.background, json.dumps(profile.industries),
            profile.budget_min, profile.budget_max,
            profile.revenue_min, profile.revenue_max,
            json.dumps(profile.location_preference),
            json.dumps(profile.values), profile.timeline,
            json.dumps(profile.criteria) if profile.criteria else None,
            profile_id
        ))
    else:
        cursor.execute("""
            INSERT INTO buyer_profiles
            (id, user_id, background, industries, budget_min, budget_max,
             revenue_min, revenue_max, location_preference, values, timeline, criteria)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id, current_user["id"], profile.background,
            json.dumps(profile.industries), profile.budget_min, profile.budget_max,
            profile.revenue_min, profile.revenue_max,
            json.dumps(profile.location_preference),
            json.dumps(profile.values), profile.timeline,
            json.dumps(profile.criteria) if profile.criteria else None
        ))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "profile_id": profile_id}

@app.get("/onboarding/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buyer_profiles WHERE user_id = ?", (current_user["id"],))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": row["id"],
        "background": row["background"],
        "industries": json.loads(row["industries"]) if row["industries"] else [],
        "budget_min": row["budget_min"],
        "budget_max": row["budget_max"],
        "revenue_min": row["revenue_min"],
        "revenue_max": row["revenue_max"],
        "location_preference": json.loads(row["location_preference"]) if row["location_preference"] else [],
        "values": json.loads(row["values"]) if row["values"] else [],
        "timeline": row["timeline"],
        "criteria": json.loads(row["criteria"]) if row["criteria"] else None
    }

@app.get("/leads")
async def get_leads(status: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT * FROM leads 
            WHERE user_id = ? AND status = ?
            ORDER BY score DESC, created_at DESC
        """, (current_user["id"], status))
    else:
        cursor.execute("""
            SELECT * FROM leads 
            WHERE user_id = ?
            ORDER BY score DESC, created_at DESC
        """, (current_user["id"],))
    
    rows = cursor.fetchall()
    conn.close()
    
    leads = []
    for row in rows:
        lead = dict(row)
        if lead.get("ai_assessment"):
            try:
                lead["ai_assessment"] = json.loads(lead["ai_assessment"])
            except:
                pass
        leads.append(lead)
    
    return {"leads": leads}

@app.post("/leads/{lead_id}/approve")
async def approve_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE leads SET status = 'approved' 
        WHERE id = ? AND user_id = ?
    """, (lead_id, current_user["id"]))
    
    conn.commit()
    conn.close()
    
    return {"success": True}

@app.post("/leads/{lead_id}/reject")
async def reject_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE leads SET status = 'rejected' 
        WHERE id = ? AND user_id = ?
    """, (lead_id, current_user["id"]))
    
    conn.commit()
    conn.close()
    
    return {"success": True}

@app.get("/api/pipeline")
async def get_pipeline(current_user: dict = Depends(get_current_user)):
    """Get all leads in pipeline (not new/rejected)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM leads 
        WHERE user_id = ? AND status NOT IN ('new', 'rejected')
        ORDER BY score DESC, created_at DESC
    """, (current_user["id"],))
    
    leads = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"data": leads}

@app.patch("/api/scout/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: str, 
    status_update: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update lead status (for pipeline movement)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE leads SET status = ? 
        WHERE id = ? AND user_id = ?
    """, (status_update.get("status"), lead_id, current_user["id"]))
    
    conn.commit()
    conn.close()
    
    return {"success": True}

@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ?", (current_user["id"],))
    total_leads = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND status = 'new'", (current_user["id"],))
    new_leads = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM leads 
        WHERE user_id = ? AND status IN ('approved', 'outreach', 'engaged')
    """, (current_user["id"],))
    active_leads = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM email_logs WHERE user_id = ?", (current_user["id"],))
    emails_sent = cursor.fetchone()[0]
    
    # Recent activities
    cursor.execute("""
        SELECT * FROM agent_activities 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 10
    """, (current_user["id"],))
    activities = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "active_leads": active_leads,
        "emails_sent": emails_sent,
        "recent_activities": activities
    }

@app.get("/agent/config")
async def get_agent_config(current_user: dict = Depends(get_current_user)):
    config = json.loads(current_user.get("agent_config", "{}"))
    return config or {
        "daily_email_limit": 10,
        "send_window_start": "09:00",
        "send_window_end": "17:00",
        "discovery_frequency": "daily",
        "auto_approve_threshold": 0,
        "reply_handling": "manual"
    }

@app.post("/agent/config")
async def update_agent_config(config: AgentConfig, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET agent_config = ? WHERE id = ?
    """, (json.dumps(config.dict()), current_user["id"]))
    
    conn.commit()
    conn.close()
    
    return {"success": True}

@app.get("/api/settings")
async def get_settings(current_user: dict = Depends(get_current_user)):
    """Get user settings"""
    config = json.loads(current_user.get("agent_config", "{}"))
    return {
        "data": {
            "daily_email_limit": config.get("daily_email_limit", 25),
            "auto_approve_threshold": config.get("auto_approve_threshold", 0),
            "discovery_frequency": config.get("discovery_frequency", "daily"),
            "notification_email": current_user.get("email", ""),
            "notification_preferences": {
                "new_leads": True,
                "email_replies": True,
                "daily_summary": True
            }
        }
    }

@app.post("/api/settings")
async def update_settings(settings: dict, current_user: dict = Depends(get_current_user)):
    """Update user settings"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET agent_config = ? WHERE id = ?
    """, (json.dumps(settings), current_user["id"]))
    
    conn.commit()
    conn.close()
    
    return {"success": True}

# CRM Endpoints
@app.get("/api/leads/{lead_id}/notes")
async def get_lead_notes(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Get notes for a lead"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify lead belongs to user
    cursor.execute("SELECT id FROM leads WHERE id = ? AND user_id = ?", (lead_id, current_user["id"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Lead not found")
    
    cursor.execute("""
        SELECT * FROM lead_notes 
        WHERE lead_id = ? 
        ORDER BY created_at DESC
    """, (lead_id,))
    
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"data": notes}

@app.post("/api/leads/{lead_id}/notes")
async def add_lead_note(
    lead_id: str, 
    note: dict,
    current_user: dict = Depends(get_current_user)
):
    """Add a note to a lead"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify lead belongs to user
    cursor.execute("SELECT id FROM leads WHERE id = ? AND user_id = ?", (lead_id, current_user["id"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Lead not found")
    
    note_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO lead_notes (id, lead_id, content, type, created_by)
        VALUES (?, ?, ?, ?, ?)
    """, (note_id, lead_id, note.get("content"), note.get("type", "note"), current_user["id"]))
    
    # Add activity
    activity_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO lead_activities (id, lead_id, type, description, user_id)
        VALUES (?, ?, 'note_added', ?, ?)
    """, (activity_id, lead_id, f"Note added: {note.get('content', '')[:50]}...", current_user["id"]))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "note_id": note_id}

@app.get("/api/leads/{lead_id}/activities")
async def get_lead_activities(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Get activity history for a lead"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify lead belongs to user
    cursor.execute("SELECT id FROM leads WHERE id = ? AND user_id = ?", (lead_id, current_user["id"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Lead not found")
    
    cursor.execute("""
        SELECT * FROM lead_activities 
        WHERE lead_id = ? 
        ORDER BY timestamp DESC
        LIMIT 50
    """, (lead_id,))
    
    activities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"data": activities}

# WebSocket for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4001)
        return
    
    user_id = payload["sub"]
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
