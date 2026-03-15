import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sqlite3
import uuid

# Simulated business data for discovery
INDUSTRIES = [
    "Technology", "Healthcare", "Manufacturing", "Services", 
    "Retail", "Construction", "Finance", "Logistics"
]

CITIES = [
    ("Salt Lake City", "UT"), ("Provo", "UT"), ("Ogden", "UT"),
    ("Denver", "CO"), ("Boulder", "CO"), ("Colorado Springs", "CO"),
    ("Phoenix", "AZ"), ("Scottsdale", "AZ"), ("Tempe", "AZ"),
    ("Boise", "ID"), ("Portland", "OR"), ("Seattle", "WA")
]

BUSINESS_NAMES = [
    "Summit", "Alpine", "Peak", "Horizon", "Legacy", "Pioneer",
    "Heritage", "Atlas", "Vantage", "Sterling", "Evergreen", "Cascade"
]

BUSINESS_SUFFIXES = [
    "Solutions", "Services", "Group", "Holdings", "Enterprises",
    "Industries", "Partners", "Associates", "Systems", "Technologies"
]

class DiscoveryService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.is_running = False
    
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    async def discover_leads(self, user_id: str, criteria: Dict) -> List[Dict]:
        """Discover new leads based on user criteria"""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get existing lead names to avoid duplicates
        cursor.execute("SELECT name FROM leads WHERE user_id = ?", (user_id,))
        existing_names = {row[0] for row in cursor.fetchall()}
        
        discovered = []
        target_count = random.randint(3, 8)  # Discover 3-8 leads per run
        
        for _ in range(target_count):
            # Generate a business
            name = self._generate_business_name()
            if name in existing_names:
                continue
            
            city, state = random.choice(CITIES)
            industry = random.choice(criteria.get("industries", ["Technology", "Services"]))
            
            # Score based on criteria match
            score = self._calculate_score(industry, criteria)
            
            lead = {
                "id": str(uuid.uuid4()),
                "name": name,
                "industry": industry,
                "revenue": random.randint(800000, 8000000),
                "employees": random.randint(5, 150),
                "city": city,
                "state": state,
                "description": self._generate_description(name, industry),
                "score": score,
                "source": random.choice(["Registry", "Directory", "LinkedIn", "BizBuySell"]),
                "email": f"info@{name.lower().replace(' ', '')}.com",
                "phone": f"(801) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
            }
            
            # Save to database
            cursor.execute("""
                INSERT INTO leads (
                    id, user_id, name, industry, revenue, employees, 
                    city, state, description, score, status, source, 
                    email, phone, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead["id"], user_id, lead["name"], lead["industry"],
                lead["revenue"], lead["employees"], lead["city"], lead["state"],
                lead["description"], lead["score"], "new", lead["source"],
                lead["email"], lead["phone"], datetime.now().isoformat()
            ))
            
            discovered.append(lead)
        
        # Log activity
        if discovered:
            activity_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO agent_activities (user_id, type, description, timestamp)
                VALUES (?, 'discovery', ?, ?)
            """, (user_id, f"Discovered {len(discovered)} new leads", datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return discovered
    
    def _generate_business_name(self) -> str:
        """Generate a realistic business name"""
        templates = [
            f"{random.choice(BUSINESS_NAMES)} {random.choice(BUSINESS_SUFFIXES)}",
            f"{random.choice(BUSINESS_NAMES)} {random.choice(BUSINESS_NAMES)} {random.choice(BUSINESS_SUFFIXES)}",
            f"{random.choice(BUSINESS_NAMES)} {random.choice(['&', 'and'])} {random.choice(BUSINESS_NAMES)}",
        ]
        return random.choice(templates)
    
    def _generate_description(self, name: str, industry: str) -> str:
        """Generate a business description"""
        descriptions = [
            f"{name} is a well-established {industry.lower()} company serving the region for over {random.randint(10, 40)} years.",
            f"Leading {industry.lower()} provider {name} has built a strong reputation for quality and reliability.",
            f"{name} specializes in {industry.lower()} solutions with a loyal customer base and consistent revenue.",
            f"Family-owned {industry.lower()} business {name} is looking for the right buyer to continue its legacy."
        ]
        return random.choice(descriptions)
    
    def _calculate_score(self, industry: str, criteria: Dict) -> int:
        """Calculate lead score based on criteria match"""
        score = random.randint(40, 70)  # Base score
        
        # Bonus for matching industries
        if industry in criteria.get("industries", []):
            score += random.randint(10, 20)
        
        # Random variation
        score += random.randint(-5, 15)
        
        return min(100, max(0, score))
    
    async def run_discovery_job(self, user_id: str):
        """Run discovery for a single user"""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get user criteria from profile
        cursor.execute("SELECT criteria FROM onboarding_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return []
        
        criteria = json.loads(row[0]) if row[0] else {
            "industries": ["Technology", "Services"],
            "location": ["UT", "CO"]
        }
        
        leads = await self.discover_leads(user_id, criteria)
        print(f"✅ Discovered {len(leads)} leads for user {user_id}")
        return leads
    
    async def run_scheduled_discovery(self):
        """Run discovery for all active users"""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get all users with active discovery
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()
        conn.close()
        
        tasks = []
        for (user_id,) in users:
            tasks.append(self.run_discovery_job(user_id))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total = sum(len(r) for r in results if isinstance(r, list))
            print(f"✅ Total leads discovered: {total}")

async def main():
    """Run discovery manually"""
    service = DiscoveryService("./acquisitor.db")
    await service.run_scheduled_discovery()

if __name__ == "__main__":
    import json
    asyncio.run(main())
