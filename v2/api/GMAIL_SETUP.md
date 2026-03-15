# Gmail API Setup Guide for ACQUISITOR

## Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name it "ACQUISITOR Gmail" → Click "Create"

## Step 2: Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Enable"

## Step 3: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: External
   - App name: "ACQUISITOR"
   - User support email: your email
   - Developer contact: your email
   - Save and Continue (skip scopes for now)
   - Add your email as a test user
   - Save

4. Back to "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "ACQUISITOR Desktop"
   - Click "Create"

5. Click "Download JSON"
6. Rename the downloaded file to `credentials.json`

## Step 4: Place Credentials

Move the file to:
```
~/projects/silver-tsunami-real/v2/api/credentials.json
```

## Step 5: Authenticate

Run this command:
```bash
cd ~/projects/silver-tsunami-real/v2/api
python3 -c "from gmail_service import gmail_service; gmail_service.authenticate()"
```

A browser window will open. Sign in with your Gmail and approve the permissions.

## Step 6: Verify

Test sending an email:
```bash
curl -X POST http://localhost:8000/api/leads/LEAD_ID/send-email \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test from ACQUISITOR",
    "body": "This is a test email!"
  }'
```

## Troubleshooting

- If you get "app is not verified", click "Advanced" → "Go to ACQUISITOR (unsafe)"
- Token is saved to `token.pickle` - don't delete it or you'll need to re-authenticate
- Keep `credentials.json` secret - don't commit it to git
