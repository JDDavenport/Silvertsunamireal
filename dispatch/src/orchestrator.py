#!/usr/bin/env python3
"""
ACQUISITOR DISPATCH System
Autonomous orchestration with cronjobs and heartbeat
"""

import os
import json
import sqlite3
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Configuration
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "dispatch.db"
STATE_PATH = DATA_DIR / "dispatch_state.json"
LOG_PATH = DATA_DIR / "dispatch.log"

@dataclass
class BuyerProfile:
    background: str = ""
    industries: List[str] = None
    roles: List[str] = None
    acquisition_experience: str = "first-time"
    motivation: str = ""
    values: List[str] = None
    location_preference: List[str] = None
    team_preference: str = "retain"
    growth_approach: str = "stable"
    budget_min: int = 500000
    budget_max: int = 2000000
    revenue_min: int = 1000000
    revenue_max: int = 5000000
    employee_min: int = 5
    employee_max: int = 50
    financing_type: str = "financed"
    sde_multiple: float = 3.0
    
    def __post_init__(self):
        if self.industries is None:
            self.industries = []
        if self.roles is None:
            self.roles = []
        if self.values is None:
            self.values = []
        if self.location_preference is None:
            self.location_preference = ["UT"]

@dataclass
class SearchCriteria:
    industries: List[str]
    excluded_industries: List[str]
    revenue_min: int
    revenue_max: int
    employee_min: int
    employee_max: int
    locations: List[str]
    business_age_min: int = 10
    business_age_max: int = 40
    owner_situations: List[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.owner_situations is None:
            self.owner_situations = ["retirement", "transition"]
        if self.keywords is None:
            self.keywords = []

@dataclass
class Lead:
    id: str
    name: str
    industry: str
    score: int
    revenue: int
    employees: int
    city: str
    state: str
    description: str
    status: str = "new"
    email: str = ""
    phone: str = ""
    created_at: str = ""
    last_contact: str = ""
    email_sequence_step: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class Activity:
    id: str
    type: str
    lead_id: str
    lead_name: str
    description: str
    timestamp: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}

class DispatchDatabase:
    """SQLite database for DISPATCH state"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY,
                    profile_json TEXT NOT NULL,
                    criteria_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    industry TEXT,
                    score INTEGER,
                    revenue INTEGER,
                    employees INTEGER,
                    city TEXT,
                    state TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'new',
                    email TEXT,
                    phone TEXT,
                    email_sequence_step INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_contact TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS activities (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    lead_id TEXT,
                    lead_name TEXT,
                    description TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY,
                    emails_sent INTEGER DEFAULT 0,
                    emails_opened INTEGER DEFAULT 0,
                    emails_replied INTEGER DEFAULT 0,
                    calls_booked INTEGER DEFAULT 0,
                    date DATE DEFAULT CURRENT_DATE
                );
                
                CREATE TABLE IF NOT EXISTS dispatch_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
    
    def save_profile(self, profile: BuyerProfile, criteria: SearchCriteria):
        """Save buyer profile and search criteria"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO profiles (id, profile_json, criteria_json) VALUES (1, ?, ?)",
                (json.dumps(asdict(profile)), json.dumps(asdict(criteria)))
            )
    
    def get_profile(self) -> tuple:
        """Get buyer profile and criteria"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT profile_json, criteria_json FROM profiles WHERE id = 1").fetchone()
            if row:
                return json.loads(row[0]), json.loads(row[1])
            return None, None
    
    def add_lead(self, lead: Lead):
        """Add a new lead"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO leads 
                (id, name, industry, score, revenue, employees, city, state, description, 
                 status, email, phone, email_sequence_step, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead.id, lead.name, lead.industry, lead.score, lead.revenue,
                lead.employees, lead.city, lead.state, lead.description,
                lead.status, lead.email, lead.phone, lead.email_sequence_step,
                lead.created_at
            ))
    
    def get_leads(self, status: str = None) -> List[Lead]:
        """Get leads, optionally filtered by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if status:
                rows = conn.execute("SELECT * FROM leads WHERE status = ?", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM leads").fetchall()
            return [Lead(**dict(row)) for row in rows]
    
    def update_lead_status(self, lead_id: str, status: str):
        """Update lead status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE leads SET status = ? WHERE id = ?",
                (status, lead_id)
            )
    
    def add_activity(self, activity: Activity):
        """Add activity log"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO activities (id, type, lead_id, lead_name, description, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                activity.id, activity.type, activity.lead_id, activity.lead_name,
                activity.description, activity.timestamp, json.dumps(activity.metadata)
            ))
    
    def get_activities(self, limit: int = 20) -> List[Activity]:
        """Get recent activities"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM activities ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
            activities = []
            for row in rows:
                row_dict = dict(row)
                row_dict['metadata'] = json.loads(row_dict.get('metadata', '{}'))
                activities.append(Activity(**row_dict))
            return activities
    
    def update_metrics(self, emails_sent: int = 0, emails_opened: int = 0, 
                       emails_replied: int = 0, calls_booked: int = 0):
        """Update daily metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO metrics (date, emails_sent, emails_opened, emails_replied, calls_booked)
                VALUES (CURRENT_DATE, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                emails_sent = emails_sent + excluded.emails_sent,
                emails_opened = emails_opened + excluded.emails_opened,
                emails_replied = emails_replied + excluded.emails_replied,
                calls_booked = calls_booked + excluded.calls_booked
            """, (emails_sent, emails_opened, emails_replied, calls_booked))
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT SUM(emails_sent) as sent, SUM(emails_opened) as opened, " +
                "SUM(emails_replied) as replied, SUM(calls_booked) as calls FROM metrics"
            ).fetchone()
            
            total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            pipeline_leads = conn.execute(
                "SELECT COUNT(*) FROM leads WHERE status IN ('approved', 'outreach', 'engaged')"
            ).fetchone()[0]
            
            sent, opened, replied, calls = row
            sent = sent or 0
            opened = opened or 0
            replied = replied or 0
            
            open_rate = (opened / sent * 100) if sent > 0 else 0
            reply_rate = (replied / sent * 100) if sent > 0 else 0
            
            return {
                "total_leads": total_leads,
                "pipeline_leads": pipeline_leads,
                "emails_sent": sent,
                "emails_opened": opened,
                "emails_replied": replied,
                "open_rate": round(open_rate, 1),
                "reply_rate": round(reply_rate, 1),
                "calls_booked": calls or 0
            }


class LeadDiscoveryAgent:
    """Agent that discovers leads based on criteria"""
    
    def __init__(self, db: DispatchDatabase):
        self.db = db
    
    def discover_leads(self, criteria: SearchCriteria) -> List[Lead]:
        """Simulate lead discovery (in production: scrape APIs, registries)"""
        import random
        
        company_names = [
            ("Summit", "Solutions"), ("Alpine", "Services"), ("Heritage", "Group"),
            ("Legacy", "Holdings"), ("Premier", "Industries"), ("Pioneer", "Systems"),
            ("Valley", "Technologies"), ("Mountain", "Enterprises"), ("Metro", "Partners"),
            ("American", "Associates")
        ]
        
        cities = [
            ("Salt Lake City", "UT"), ("Provo", "UT"), ("Ogden", "UT"),
            ("Lehi", "UT"), ("Park City", "UT"), ("Denver", "CO"),
            ("Boulder", "CO"), ("Phoenix", "AZ"), ("Boise", "ID")
        ]
        
        leads = []
        for i in range(random.randint(5, 12)):
            name_parts = random.choice(company_names)
            city, state = random.choice(cities)
            industry = random.choice(criteria.industries) if criteria.industries else "Services"
            
            revenue = random.randint(criteria.revenue_min, criteria.revenue_max)
            employees = random.randint(criteria.employee_min, criteria.employee_max)
            score = random.randint(70, 95)
            
            lead = Lead(
                id=f"lead_{int(time.time())}_{i}",
                name=f"{name_parts[0]} {name_parts[1]}",
                industry=industry,
                score=score,
                revenue=revenue,
                employees=employees,
                city=city,
                state=state,
                description=f"{industry} business with {employees} employees. Owner looking to retire after {random.randint(10, 30)} years. Strong local reputation.",
                email=f"owner@{name_parts[0].lower()}{name_parts[1].lower()}.com",
                status="new"
            )
            leads.append(lead)
            self.db.add_lead(lead)
        
        return leads


class OutreachAgent:
    """Agent that handles email outreach"""
    
    def __init__(self, db: DispatchDatabase):
        self.db = db
        self.sequence_templates = {
            0: {
                "subject": "Question about {company_name}",
                "body": """Hi {owner_name},

I came across {company_name} and was impressed by your {industry} reputation in {city}.

I'm an entrepreneur looking to acquire and grow a business in the {region} area. Your company caught my attention because of {specific_reason}.

Would you be open to a brief conversation about your future plans for the business? No pressure — just exploring if there might be a fit.

Best regards,
JD
"""
            },
            1: {
                "subject": "Follow-up: {company_name}",
                "body": """Hi {owner_name},

Quick follow-up on my note from a few days ago about {company_name}.

I understand you're likely busy running the business. I'm serious about finding the right acquisition opportunity and {company_name} remains at the top of my list.

If now isn't the right time, I completely understand. But if you'd be open to a 15-minute call to explore possibilities, I'd appreciate the conversation.

Best,
JD
"""
            },
            2: {
                "subject": "One last attempt re: {company_name}",
                "body": """Hi {owner_name},

I'll keep this brief — I know you get a lot of emails.

I'm still very interested in {company_name} as a potential acquisition. If you're considering a transition in the next 1-2 years, I'd love to chat.

If not, no worries. I'll step back and wish you continued success.

Best,
JD
"""
            }
        }
    
    def send_email(self, lead: Lead, step: int) -> bool:
        """Simulate sending email (in production: Gmail API, SendGrid, etc.)"""
        template = self.sequence_templates.get(step, self.sequence_templates[0])
        
        # Log the activity
        activity = Activity(
            id=f"act_{int(time.time())}_{lead.id}",
            type="email_sent",
            lead_id=lead.id,
            lead_name=lead.name,
            description=f"Sent Day {step * 3} email to {lead.name}",
            metadata={"step": step, "subject": template["subject"].format(company_name=lead.name)}
        )
        self.db.add_activity(activity)
        self.db.update_metrics(emails_sent=1)
        
        # Simulate 30% open rate
        import random
        if random.random() < 0.3:
            self.db.update_metrics(emails_opened=1)
        
        return True
    
    def process_replies(self):
        """Simulate checking for replies (in production: Gmail API polling)"""
        import random
        
        # Get leads in outreach
        leads = self.db.get_leads("outreach")
        
        for lead in leads:
            # Simulate 15% reply rate
            if random.random() < 0.15:
                reply_types = ["interested", "not_interested", "call_later", "question"]
                reply_type = random.choice(reply_types)
                
                if reply_type == "interested":
                    self.db.update_lead_status(lead.id, "engaged")
                    description = f"Positive reply from {lead.name} - interested in call"
                    self.db.update_metrics(emails_replied=1)
                elif reply_type == "not_interested":
                    self.db.update_lead_status(lead.id, "rejected")
                    description = f"Reply from {lead.name} - not interested"
                else:
                    description = f"Reply from {lead.name} - {reply_type.replace('_', ' ')}"
                
                activity = Activity(
                    id=f"act_{int(time.time())}_{lead.id}_reply",
                    type="email_replied",
                    lead_id=lead.id,
                    lead_name=lead.name,
                    description=description,
                    metadata={"reply_type": reply_type}
                )
                self.db.add_activity(activity)


class DispatchOrchestrator:
    """Main orchestrator with cronjob scheduling and heartbeat"""
    
    def __init__(self):
        self.db = DispatchDatabase(DB_PATH)
        self.discovery = LeadDiscoveryAgent(self.db)
        self.outreach = OutreachAgent(self.db)
        self.active = False
        self.last_heartbeat = None
        
        # Setup scheduled jobs
        self._setup_schedule()
    
    def _setup_schedule(self):
        """Setup cron-like schedule"""
        # Daily discovery at 6 AM
        schedule.every().day.at("06:00").do(self.job_daily_discovery)
        
        # Outreach execution every 30 minutes during business hours
        schedule.every(30).minutes.do(self.job_outreach_execution)
        
        # Reply checking every 15 minutes
        schedule.every(15).minutes.do(self.job_check_replies)
        
        # Daily summary at 8 AM
        schedule.every().day.at("08:00").do(self.job_daily_summary)
        
        # Pipeline review at 6 PM
        schedule.every().day.at("18:00").do(self.job_pipeline_review)
    
    def job_daily_discovery(self):
        """6 AM: Discover new leads"""
        print(f"[{datetime.now()}] 🔍 Running daily discovery...")
        
        _, criteria = self.db.get_profile()
        if criteria:
            leads = self.discovery.discover_leads(SearchCriteria(**criteria))
            print(f"  Discovered {len(leads)} new leads")
            
            # Log activity
            activity = Activity(
                id=f"act_{int(time.time())}_discovery",
                type="lead_discovered",
                lead_id="",
                lead_name="Discovery Run",
                description=f"Discovered {len(leads)} new leads matching criteria",
                metadata={"count": len(leads)}
            )
            self.db.add_activity(activity)
    
    def job_outreach_execution(self):
        """Every 30 min: Send emails to approved leads"""
        # Only run during business hours (9 AM - 6 PM)
        hour = datetime.now().hour
        if hour < 9 or hour >= 18:
            return
        
        print(f"[{datetime.now()}] 📧 Running outreach execution...")
        
        # Get approved leads that haven't been contacted
        leads = self.db.get_leads("approved")
        
        # Limit to 25 emails per day (spread across runs)
        for lead in leads[:3]:  # Send ~3 per run
            self.outreach.send_email(lead, lead.email_sequence_step)
            self.db.update_lead_status(lead.id, "outreach")
            print(f"  Sent email to {lead.name}")
    
    def job_check_replies(self):
        """Every 15 min: Check for email replies"""
        print(f"[{datetime.now()}] 💬 Checking for replies...")
        self.outreach.process_replies()
    
    def job_daily_summary(self):
        """8 AM: Send daily summary"""
        print(f"[{datetime.now()}] 📊 Generating daily summary...")
        
        metrics = self.db.get_metrics()
        activities = self.db.get_activities(5)
        
        summary = f"""
📊 ACQUISITOR Daily Summary

🔍 Discovery:
   • {metrics['total_leads']} total leads
   • {metrics['pipeline_leads']} in pipeline

📧 Outreach (Last 24h):
   • {metrics['emails_sent']} emails sent
   • {metrics['open_rate']}% open rate
   • {metrics['reply_rate']}% reply rate
   • {metrics['calls_booked']} calls booked

⚡ Recent Activity:
"""
        for act in activities[:3]:
            summary += f"   • {act.description}\n"
        
        print(summary)
        
        # In production: Send to Telegram, email, etc.
        self._send_notification(summary)
    
    def job_pipeline_review(self):
        """6 PM: Review pipeline and plan next day"""
        print(f"[{datetime.now()}] 📋 Running pipeline review...")
        
        engaged = self.db.get_leads("engaged")
        
        for lead in engaged:
            # Check if we should book a call
            activity = Activity(
                id=f"act_{int(time.time())}_{lead.id}_booking",
                type="call_scheduled",
                lead_id=lead.id,
                lead_name=lead.name,
                description=f"Discovery call initiated with {lead.name}",
                metadata={"status": "pending_confirmation"}
            )
            self.db.add_activity(activity)
            self.db.update_metrics(calls_booked=1)
            print(f"  Booking call with {lead.name}")
    
    def _send_notification(self, message: str):
        """Send notification to user (Telegram, email, etc.)"""
        # In production: Integrate with Telegram bot
        pass
    
    def heartbeat(self):
        """Main heartbeat loop - runs every minute"""
        self.last_heartbeat = datetime.now()
        schedule.run_pending()
    
    def run(self):
        """Main run loop"""
        print("🤖 ACQUISITOR DISPATCH System Starting...")
        print(f"   Database: {DB_PATH}")
        print(f"   Schedule: {len(schedule.jobs)} jobs configured")
        print("")
        print("Scheduled Jobs:")
        for job in schedule.jobs:
            print(f"  • {job}")
        print("")
        print("Running heartbeat loop (Ctrl+C to stop)...")
        
        self.active = True
        try:
            while self.active:
                self.heartbeat()
                time.sleep(60)  # 1 minute heartbeat
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            self.active = False
    
    def activate(self, profile: BuyerProfile, criteria: SearchCriteria, leads: List[Lead]):
        """Activate automation with buyer profile"""
        print("⚡ Activating DISPATCH automation...")
        
        # Save profile and criteria
        self.db.save_profile(profile, criteria)
        
        # Add initial leads
        for lead in leads:
            self.db.add_lead(lead)
        
        print(f"  ✓ Saved profile for {profile.background[:50]}...")
        print(f"  ✓ Added {len(leads)} leads to database")
        print(f"  ✓ Automation active")
        
        # Log activation
        activity = Activity(
            id=f"act_{int(time.time())}_activation",
            type="system",
            lead_id="",
            lead_name="System",
            description="Autonomous outreach activated",
            metadata={"lead_count": len(leads)}
        )
        self.db.add_activity(activity)
        
        return {"success": True, "message": "Automation activated"}


# Flask API for frontend integration
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
orchestrator = DispatchOrchestrator()

@app.route('/api/intake/activate', methods=['POST'])
def api_activate():
    """Activate automation from frontend"""
    data = request.json
    
    profile_data = data.get('profile', {})
    criteria_data = data.get('criteria', {})
    leads_data = data.get('leads', [])
    
    profile = BuyerProfile(
        background=profile_data.get('background', ''),
        industries=profile_data.get('industries', []),
        acquisition_experience=profile_data.get('acquisitionExperience', 'first-time'),
        motivation=profile_data.get('motivation', ''),
        values=profile_data.get('values', []),
        location_preference=profile_data.get('locationPreference', ['UT']),
        budget_min=profile_data.get('budget', {}).get('min', 500000),
        budget_max=profile_data.get('budget', {}).get('max', 2000000),
        revenue_min=profile_data.get('revenueRange', {}).get('min', 1000000),
        revenue_max=profile_data.get('revenueRange', {}).get('max', 5000000),
        employee_min=profile_data.get('employeeRange', {}).get('min', 5),
        employee_max=profile_data.get('employeeRange', {}).get('max', 50),
    )
    
    criteria = SearchCriteria(
        industries=criteria_data.get('industries', ['Services']),
        excluded_industries=criteria_data.get('excludedIndustries', []),
        revenue_min=criteria_data.get('revenueRange', {}).get('min', 1000000),
        revenue_max=criteria_data.get('revenueRange', {}).get('max', 5000000),
        employee_min=criteria_data.get('employeeRange', {}).get('min', 5),
        employee_max=criteria_data.get('employeeRange', {}).get('max', 50),
        locations=criteria_data.get('locationPreference', ['UT']),
    )
    
    leads = [Lead(**lead) for lead in leads_data]
    
    result = orchestrator.activate(profile, criteria, leads)
    return jsonify({"success": True, "data": result})

@app.route('/api/scout/leads', methods=['GET'])
def api_get_leads():
    """Get all leads"""
    status = request.args.get('status')
    leads = orchestrator.db.get_leads(status)
    return jsonify({
        "success": True,
        "data": [asdict(lead) for lead in leads],
        "meta": {"total": len(leads)}
    })

@app.route('/api/pipeline', methods=['GET'])
def api_get_pipeline():
    """Get pipeline leads"""
    leads = orchestrator.db.get_leads()
    return jsonify({
        "success": True,
        "data": [asdict(lead) for lead in leads if lead.status in ['approved', 'outreach', 'engaged', 'qualified']]
    })

@app.route('/api/metrics', methods=['GET'])
def api_get_metrics():
    """Get current metrics"""
    metrics = orchestrator.db.get_metrics()
    return jsonify({"success": True, "data": metrics})

@app.route('/api/activity', methods=['GET'])
def api_get_activities():
    """Get recent activities"""
    limit = request.args.get('limit', 20, type=int)
    activities = orchestrator.db.get_activities(limit)
    return jsonify({
        "success": True,
        "data": [asdict(act) for act in activities]
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check"""
    return jsonify({
        "success": True,
        "data": {
            "status": "healthy",
            "active": orchestrator.active,
            "last_heartbeat": orchestrator.last_heartbeat.isoformat() if orchestrator.last_heartbeat else None,
            "scheduled_jobs": len(schedule.jobs)
        }
    })


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        # Run Flask API server
        print("🌐 Starting DISPATCH API server on port 3001...")
        app.run(host='0.0.0.0', port=3001, debug=True)
    else:
        # Run orchestrator daemon
        orchestrator.run()
