import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import Optional, List, Dict
import pickle
from pathlib import Path

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailService:
    """Gmail API integration for sending and receiving emails"""
    
    def __init__(self):
        self.credentials_path = os.getenv(
            'GOOGLE_CREDENTIALS_PATH', 
            str(Path(__file__).parent / 'credentials.json')
        )
        self.token_path = os.getenv(
            'GOOGLE_TOKEN_PATH',
            str(Path(__file__).parent / 'token.pickle')
        )
        self.service = None
        self.user_email = None
    
    def is_authenticated(self) -> bool:
        """Check if we have valid credentials"""
        if not os.path.exists(self.token_path):
            return False
        
        try:
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
            return creds and creds.valid
        except:
            return False
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API - requires user interaction first time"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                creds = None
        
        # Need new authentication
        if not creds or not creds.valid:
            if not os.path.exists(self.credentials_path):
                print(f"❌ Credentials file not found: {self.credentials_path}")
                print("   Create one at https://console.cloud.google.com/apis/credentials")
                return False
            
            print("🔐 Starting Gmail authentication flow...")
            print("   A browser window will open. Please authorize the application.")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save token
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                
                print("✅ Gmail authentication successful!")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return False
        
        # Build service
        self.service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
        
        # Get user email
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            self.user_email = profile.get('emailAddress')
            print(f"✅ Connected to Gmail: {self.user_email}")
        except Exception as e:
            print(f"Warning: Could not get profile: {e}")
        
        return True
    
    def send_email(
        self, 
        to: str, 
        subject: str, 
        body: str, 
        html: bool = False,
        cc: List[str] = None,
        bcc: List[str] = None
    ) -> Optional[str]:
        """Send an email via Gmail API"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            # Create message
            if html:
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(body, 'html'))
                # Also add plain text version
                plain_text = self._html_to_text(body)
                msg.attach(MIMEText(plain_text, 'plain'))
            else:
                msg = MIMEText(body, 'plain')
            
            msg['to'] = to
            msg['subject'] = subject
            
            if self.user_email:
                msg['from'] = self.user_email
            
            if cc:
                msg['cc'] = ', '.join(cc)
            if bcc:
                msg['bcc'] = ', '.join(bcc)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            body_data = {'raw': raw_message}
            
            message = self.service.users().messages().send(
                userId='me', 
                body=body_data
            ).execute()
            
            print(f"✅ Email sent to {to}: {message['id']}")
            return message['id']
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return None
    
    def get_inbox(self, max_results: int = 10, query: str = '') -> List[Dict]:
        """Get recent inbox messages"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full message details
            full_messages = []
            for msg in messages:
                try:
                    detail = self.service.users().messages().get(
                        userId='me', 
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'From', 'Date']
                    ).execute()
                    
                    headers = {h['name']: h['value'] for h in detail.get('payload', {}).get('headers', [])}
                    
                    full_messages.append({
                        'id': msg['id'],
                        'threadId': msg.get('threadId'),
                        'subject': headers.get('Subject', 'No Subject'),
                        'from': headers.get('From', 'Unknown'),
                        'date': headers.get('Date', ''),
                        'snippet': detail.get('snippet', '')
                    })
                except Exception as e:
                    print(f"Error getting message details: {e}")
                    continue
            
            return full_messages
            
        except Exception as e:
            print(f"❌ Failed to get inbox: {e}")
            return []
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get full message content"""
        if not self.service:
            return None
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            return message
        except Exception as e:
            print(f"❌ Failed to get message: {e}")
            return None
    
    def _html_to_text(self, html: str) -> str:
        """Simple HTML to text conversion"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Convert HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        return text

# Singleton instance
gmail_service = GmailService()

if __name__ == "__main__":
    # Test
    print("Testing Gmail Service...")
    
    if gmail_service.authenticate():
        print("\n✅ Authentication successful!")
        
        # Test send (commented out to prevent accidental sends)
        # result = gmail_service.send_email(
        #     to="test@example.com",
        #     subject="Test from ACQUISITOR",
        #     body="This is a test email from your ACQUISITOR agent!"
        # )
        
        # Test inbox
        messages = gmail_service.get_inbox(max_results=5)
        print(f"\n📧 Found {len(messages)} messages in inbox")
        for m in messages[:3]:
            print(f"  - {m['subject'][:50]}... from {m['from'][:30]}")
    else:
        print("\n❌ Authentication failed")
