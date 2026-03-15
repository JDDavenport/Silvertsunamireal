import os
import json
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import Optional
import pickle

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self, credentials_path: str = None, token_path: str = None):
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH', './credentials.json')
        self.token_path = token_path or os.getenv('GOOGLE_TOKEN_PATH', './token.pickle')
        self.service = None
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get them
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"❌ Credentials file not found: {self.credentials_path}")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for future runs
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def send_email(self, to: str, subject: str, body: str, 
                   html: bool = False, from_name: str = None) -> Optional[str]:
        """Send an email via Gmail API"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            # Create message
            if html:
                msg = MIMEText(body, 'html')
            else:
                msg = MIMEText(body, 'plain')
            
            msg['to'] = to
            msg['subject'] = subject
            
            if from_name:
                msg['from'] = from_name
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            body_data = {'raw': raw_message}
            
            message = self.service.users().messages().send(
                userId='me', 
                body=body_data
            ).execute()
            
            return message['id']
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return None
    
    def get_inbox(self, max_results: int = 10) -> list:
        """Get recent inbox messages"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            return messages
            
        except Exception as e:
            print(f"❌ Failed to get inbox: {e}")
            return []

# Singleton instance
gmail_service = GmailService()

if __name__ == "__main__":
    # Test sending
    result = gmail_service.send_email(
        to="test@example.com",
        subject="Test from ACQUISITOR",
        body="This is a test email from your ACQUISITOR agent!"
    )
    if result:
        print(f"✅ Email sent! Message ID: {result}")
    else:
        print("❌ Failed to send email")
