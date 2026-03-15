import csv
import io
from typing import List, Dict
import uuid
from datetime import datetime
import sqlite3

class CSVImporter:
    """Import leads from CSV files"""
    
    # Expected columns (flexible mapping)
    COLUMN_MAPPINGS = {
        'name': ['name', 'business_name', 'company', 'company_name', 'title', 'business name'],
        'industry': ['industry', 'sector', 'category', 'business_type', 'business type'],
        'revenue': ['revenue', 'annual_revenue', 'sales', 'gross_revenue', 'annual revenue'],
        'employees': ['employees', 'employee_count', 'staff', 'team_size', 'employee count'],
        'city': ['city', 'town', 'municipality'],
        'state': ['state', 'province', 'region'],
        'description': ['description', 'about', 'notes', 'summary'],
        'email': ['email', 'e-mail', 'email_address', 'contact_email', 'email address'],
        'phone': ['phone', 'telephone', 'contact_phone', 'phone_number', 'contact phone'],
        'website': ['website', 'url', 'site', 'web'],
        'source': ['source', 'lead_source', 'origin'],
        'score': ['score', 'rating', 'grade']
    }
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def detect_columns(self, headers: List[str]) -> Dict[str, str]:
        """Detect which CSV columns map to our fields"""
        mapping = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        for field, possible_names in self.COLUMN_MAPPINGS.items():
            for name in possible_names:
                if name in headers_lower:
                    mapping[field] = headers[headers_lower.index(name)]
                    break
        
        return mapping
    
    def parse_csv(self, csv_content: str, user_id: str) -> Dict:
        """Parse CSV and return leads + stats"""
        leads = []
        errors = []
        
        try:
            # Parse CSV
            reader = csv.DictReader(io.StringIO(csv_content))
            headers = reader.fieldnames or []
            
            # Detect column mapping
            column_map = self.detect_columns(headers)
            
            if not column_map.get('name'):
                return {
                    'success': False,
                    'error': 'Could not detect business name column. Expected one of: ' + 
                            ', '.join(self.COLUMN_MAPPINGS['name'])
                }
            
            # Process each row
            for i, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                try:
                    lead = self._row_to_lead(row, column_map, user_id)
                    if lead:
                        leads.append(lead)
                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")
            
            return {
                'success': True,
                'leads': leads,
                'count': len(leads),
                'errors': errors,
                'column_mapping': column_map
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _row_to_lead(self, row: Dict, column_map: Dict, user_id: str) -> Dict:
        """Convert CSV row to lead dict"""
        name = row.get(column_map.get('name', ''), '').strip()
        if not name:
            return None
        
        # Parse revenue (handle various formats)
        revenue_str = row.get(column_map.get('revenue', ''), '0')
        revenue = self._parse_revenue(revenue_str)
        
        # Parse employees
        employees_str = row.get(column_map.get('employees', ''), '0')
        employees = self._parse_number(employees_str)
        
        # Parse score
        score_str = row.get(column_map.get('score', ''), '0')
        score = self._parse_number(score_str) or 50  # Default 50
        
        lead = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': name,
            'industry': row.get(column_map.get('industry', ''), 'Unknown'),
            'revenue': revenue,
            'employees': employees,
            'city': row.get(column_map.get('city', ''), ''),
            'state': row.get(column_map.get('state', ''), 'UT'),
            'description': row.get(column_map.get('description', ''), ''),
            'email': row.get(column_map.get('email', ''), None),
            'phone': row.get(column_map.get('phone', ''), None),
            'website': row.get(column_map.get('website', ''), None),
            'score': min(100, max(0, score)),
            'status': 'new',
            'source': row.get(column_map.get('source', ''), 'CSV Import'),
            'created_at': datetime.now().isoformat()
        }
        
        return lead
    
    def _parse_revenue(self, value: str) -> int:
        """Parse revenue from various formats"""
        if not value:
            return 0
        
        # Remove $, commas, spaces
        clean = value.replace('$', '').replace(',', '').replace(' ', '').strip()
        
        # Handle K/M/B suffixes
        clean = clean.lower()
        multiplier = 1
        
        if clean.endswith('k'):
            multiplier = 1000
            clean = clean[:-1]
        elif clean.endswith('m'):
            multiplier = 1000000
            clean = clean[:-1]
        elif clean.endswith('b'):
            multiplier = 1000000000
            clean = clean[:-1]
        
        try:
            return int(float(clean) * multiplier)
        except:
            return 0
    
    def _parse_number(self, value: str) -> int:
        """Parse number from string"""
        if not value:
            return 0
        
        # Remove non-numeric characters except decimal
        clean = ''.join(c for c in value if c.isdigit() or c == '.')
        
        try:
            return int(float(clean))
        except:
            return 0
    
    def save_leads(self, leads: List[Dict]) -> int:
        """Save leads to database"""
        conn = self.get_db()
        cursor = conn.cursor()
        
        saved = 0
        for lead in leads:
            try:
                # Check for duplicates (same name + city)
                cursor.execute("""
                    SELECT id FROM leads 
                    WHERE user_id = ? AND name = ? AND city = ?
                """, (lead['user_id'], lead['name'], lead['city']))
                
                if cursor.fetchone():
                    continue  # Skip duplicate
                
                cursor.execute("""
                    INSERT INTO leads (
                        id, user_id, name, industry, revenue, employees,
                        city, state, description, score, status, source,
                        email, phone, website, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead['id'], lead['user_id'], lead['name'], lead['industry'],
                    lead['revenue'], lead['employees'], lead['city'], lead['state'],
                    lead['description'], lead['score'], lead['status'], lead['source'],
                    lead['email'], lead['phone'], lead['website'], lead['created_at']
                ))
                
                saved += 1
                
            except Exception as e:
                print(f"Error saving lead {lead['name']}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return saved

# Example CSV formats supported:
UTAH_CORPS_CSV = """Business Name,Entity Type,Registration Date,City,State
ABC Technology LLC,LLC,01/15/2005,Salt Lake City,UT
Summit Services Inc,CORPORATION,03/22/1998,Provo,UT
"""

BIZBUysell_CSV = """Title,Revenue,City,State,Asking Price
Alpine Auto Repair,$1.2M,Salt Lake City,UT,$850K
TechFlow Solutions,$2.5M,Provo,UT,$1.8M
"""

ZOOMINFO_CSV = """Company Name,Industry,Revenue (USD),Employees,City,State
Peak Manufacturing,Manufacturing,5000000,45,Ogden,UT
Horizon Consulting,Services,3200000,12,Salt Lake City,UT
"""
