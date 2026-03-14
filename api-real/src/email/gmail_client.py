"""
Gmail Integration - Real Email Sending and Monitoring
Uses Gmail API for outreach and reply tracking
"""

import os
import base64
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.readonly'
]

class GmailClient:
    """Gmail API client for sending and monitoring emails"""
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"❌ Credentials file not found: {self.credentials_path}")
                    print("   Download from Google Cloud Console → APIs & Services → Credentials")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.authenticated = True
            
            # Get user info
            profile = self.service.users().getProfile(userId='me').execute()
            print(f"✅ Gmail authenticated: {profile.get('emailAddress', 'Unknown')}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail authentication failed: {e}")
            return False
    
    def send_email(self, to: str, subject: str, body: str, 
                   reply_to_thread: Optional[str] = None) -> Optional[Dict]:
        """
        Send an email via Gmail API
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (plain text)
            reply_to_thread: Gmail thread ID if replying to existing thread
        
        Returns:
            Dict with message_id, thread_id, or None if failed
        """
        if not self.authenticated:
            print("❌ Not authenticated. Call authenticate() first.")
            return None
        
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            message['from'] = 'me'
            
            if reply_to_thread:
                message['In-Reply-To'] = reply_to_thread
                message['References'] = reply_to_thread
            
            # Encode
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message, 'threadId': reply_to_thread} if reply_to_thread else {'raw': raw_message}
            ).execute()
            
            print(f"✅ Email sent to {to}")
            print(f"   Subject: {subject}")
            print(f"   Message ID: {result['id']}")
            
            return {
                'message_id': result['id'],
                'thread_id': result.get('threadId'),
                'to': to,
                'subject': subject,
                'sent_at': datetime.now().isoformat()
            }
            
        except HttpError as e:
            print(f"❌ Failed to send email: {e}")
            return None
    
    def check_replies(self, since_hours: int = 1) -> List[Dict]:
        """
        Check for new replies in inbox
        
        Args:
            since_hours: Only check messages from last N hours
        
        Returns:
            List of reply dicts with thread_id, from, subject, body
        """
        if not self.authenticated:
            print("❌ Not authenticated")
            return []
        
        try:
            # Build query
            since = datetime.now() - timedelta(hours=since_hours)
            since_str = since.strftime('%Y/%m/%d')
            query = f'after:{since_str} in:inbox -from:me'
            
            # Search messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            
            replies = []
            for msg_meta in messages:
                try:
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=msg_meta['id'],
                        format='full'
                    ).execute()
                    
                    # Extract headers
                    headers = msg.get('payload', {}).get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    
                    # Extract body
                    body = self._extract_body(msg)
                    
                    # Check if this is a reply (has Re: in subject or is in thread)
                    if 'Re:' in subject or msg.get('threadId') != msg['id']:
                        replies.append({
                            'message_id': msg['id'],
                            'thread_id': msg.get('threadId'),
                            'from': from_addr,
                            'subject': subject,
                            'body': body,
                            'received_at': datetime.fromtimestamp(int(msg['internalDate']) / 1000).isoformat()
                        })
                
                except Exception as e:
                    print(f"Error processing message {msg_meta['id']}: {e}")
                    continue
            
            print(f"✅ Found {len(replies)} replies")
            return replies
            
        except HttpError as e:
            print(f"❌ Failed to check replies: {e}")
            return []
    
    def _extract_body(self, message: Dict) -> str:
        """Extract plain text body from Gmail message"""
        parts = message.get('payload', {}).get('parts', [])
        
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            elif part.get('mimeType') == 'text/html':
                # Skip HTML for now, prefer plain text
                continue
            elif 'parts' in part:
                # Recurse into nested parts
                nested = self._extract_body({'payload': part})
                if nested:
                    return nested
        
        # If no parts, check body directly
        data = message.get('payload', {}).get('body', {}).get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
        
        return ""
    
    def get_thread(self, thread_id: str) -> List[Dict]:
        """Get all messages in a thread"""
        if not self.authenticated:
            return []
        
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = []
            for msg in thread.get('messages', []):
                headers = msg.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                messages.append({
                    'message_id': msg['id'],
                    'from': from_addr,
                    'subject': subject,
                    'body': self._extract_body(msg),
                    'timestamp': datetime.fromtimestamp(int(msg['internalDate']) / 1000).isoformat()
                })
            
            return messages
            
        except HttpError as e:
            print(f"❌ Failed to get thread: {e}")
            return []
    
    def create_draft(self, to: str, subject: str, body: str) -> Optional[str]:
        """Create email draft for review"""
        if not self.authenticated:
            return None
        
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()
            
            print(f"✅ Draft created for {to}")
            return draft['id']
            
        except HttpError as e:
            print(f"❌ Failed to create draft: {e}")
            return None


# Setup helper
def setup_gmail_credentials():
    """Instructions for setting up Gmail API credentials"""
    print("""
📧 Gmail API Setup Instructions

1. Go to https://console.cloud.google.com/
2. Create new project (or select existing)
3. Enable Gmail API:
   - APIs & Services → Library
   - Search "Gmail API" → Enable

4. Create OAuth credentials:
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: Desktop app
   - Name: ACQUISITOR
   - Download JSON → Save as 'credentials.json' in this directory

5. Run authenticate() to generate token.json

6. First time will open browser for Google login approval

Note: For production, app needs verification by Google for public use.
For demo/personal use, you can use it in "testing" mode.
""")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup_gmail_credentials()
    else:
        # Test
        client = GmailClient()
        
        if client.authenticate():
            print("\n✅ Gmail integration ready!")
            print("\nTest commands:")
            print("  - client.send_email('recipient@example.com', 'Subject', 'Body')")
            print("  - client.check_replies(since_hours=24)")
        else:
            print("\n❌ Authentication failed. Run: python gmail_client.py setup")
