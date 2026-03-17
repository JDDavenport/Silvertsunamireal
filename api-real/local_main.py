# Local SQLite version for quick deploy
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import aiosqlite
import uuid

# Create local SQLite database
DB_PATH = "acquisitor_local.db"
JWT_SECRET = os.getenv("JWT_SECRET", "local-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"

app = FastAPI(title="ACQUISITOR API (Local)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                business_name TEXT NOT NULL,
                owner_name TEXT,
                owner_email TEXT,
                industry TEXT,
                revenue INTEGER,
                status TEXT DEFAULT 'new',
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        await db.commit()

@app.on_event("startup")
async def startup():
    await init_db()

# Auth
async def get_current_user(token: str = None):
    if not token:
        # For local dev, create a test user
        return {"id": "test-user-123", "email": "test@acquisitor.com"}
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"id": payload.get("sub"), "email": payload.get("email")}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/health")
async def health():
    return {"status": "ok", "mode": "local"}

@app.get("/")
async def root():
    return {"message": "ACQUISITOR API - Local Development"}

@app.get("/leads")
async def list_leads(user: dict = Depends(get_current_user)):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM leads WHERE user_id = ? ORDER BY created_at DESC",
            (user["id"],)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

@app.post("/leads")
async def create_lead(lead: dict, user: dict = Depends(get_current_user)):
    lead_id = str(uuid.uuid4())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO leads (id, user_id, business_name, owner_name, owner_email, industry, revenue, score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (lead_id, user["id"], lead.get("business_name"), lead.get("owner_name"),
             lead.get("owner_email"), lead.get("industry"), lead.get("revenue"), lead.get("score", 0))
        )
        await db.commit()
    return {"id": lead_id, "message": "Lead created"}

@app.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
