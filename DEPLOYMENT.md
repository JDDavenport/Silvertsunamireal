# ACQUISITOR Backend Deployment Summary

## ✅ Code Status

### Changes Committed to GitHub
- **Repository:** https://github.com/JDDavenport/Silvertsunamireal
- **Branch:** master
- **Commit:** 210b226 - Deploy: ACQUISITOR production API with auth and database

### Files Updated
1. `api-real/src/main.py` - Production API with full auth
2. `api-real/Dockerfile` - Docker config for Render
3. `api-real/requirements.txt` - Added auth dependencies
4. `api-real/render.yaml` - Render deployment blueprint
5. `api-real/.env.example` - Environment documentation

---

## 🔧 API Features Implemented

### Authentication
- `POST /auth/google` - Google OAuth login
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout

### Leads Management
- `GET /leads` - List all leads (with filters)
- `POST /leads` - Create new lead
- `GET /leads/{id}` - Get single lead
- `PATCH /leads/{id}` - Update lead

### Pipeline
- `GET /pipeline` - Get pipeline stages with leads

### Legacy API (for existing frontend)
- `GET /api/scout/leads`
- `POST /api/scout/leads`
- `GET /api/pipeline`
- `GET /api/activity`
- `GET /api/metrics`

### Health Check
- `GET /health` - Database connectivity check

---

## 🚀 Deployment Options

### Option 1: Render (Recommended - matches frontend config)

The frontend expects API at: `https://acquisitor-api.onrender.com`

**Steps:**
1. Go to https://dashboard.render.com/
2. Click "New +" → "Blueprint"
3. Connect GitHub repo: `JDDavenport/Silvertsunamireal`
4. Select `api-real/render.yaml`
5. Render will auto-create:
   - Web service (Docker deployment)
   - PostgreSQL database

**Set Environment Variables:**
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FRONTEND_URL=https://acquisitor.vercel.app
```

**Get Google OAuth Credentials:**
1. Go to https://console.cloud.google.com/apis/credentials
2. Create project "ACQUISITOR"
3. Create OAuth 2.0 Client ID (Web application)
4. Add authorized origins:
   - `https://acquisitor.vercel.app`
   - `https://acquisitor-api.onrender.com`
5. Add redirect URI:
   - `https://acquisitor-api.onrender.com/auth/google`

---

### Option 2: Railway

**Steps:**
```bash
cd ~/projects/silver-tsunami-real/api-real
railway login
railway link
railway add --database postgresql
railway up
```

**Set Variables:**
```bash
railway vars set JWT_SECRET=$(openssl rand -hex 32)
railway vars set GOOGLE_CLIENT_ID=your-client-id
railway vars set GOOGLE_CLIENT_SECRET=your-client-secret
railway vars set FRONTEND_URL=https://acquisitor.vercel.app
```

---

## 📋 Environment Variables Required

| Variable | Description | Source |
|----------|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection | Auto-generated |
| `JWT_SECRET` | JWT signing key | Generate or auto |
| `GOOGLE_CLIENT_ID` | Google OAuth ID | Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Secret | Google Cloud Console |
| `FRONTEND_URL` | Vercel frontend URL | `https://acquisitor.vercel.app` |

---

## ✅ Success Criteria Checklist

- [ ] API responds 200 OK at `/health`
- [ ] Database connected and migrations run
- [ ] Google OAuth working
- [ ] Can create/fetch user data
- [ ] CORS allows frontend domain
- [ ] Frontend `VITE_API_URL` updated

---

## 🔍 Testing After Deploy

```bash
# Health check
curl https://acquisitor-api.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-..."
}
```

---

## ⚠️ Notes

1. **Database Migrations:** The API auto-creates tables on first run
2. **CORS:** Configured for `FRONTEND_URL` + localhost for development
3. **JWT Tokens:** 7-day expiration, stored in localStorage on frontend
4. **Port:** Uses `$PORT` env var (Render) or defaults to 8000

---

## 🔄 Next Steps for Main Agent

1. **Deploy to Render:**
   - Use the Blueprint at `api-real/render.yaml`
   - Or create web service manually with Docker

2. **Configure Google OAuth:**
   - Create credentials in Google Cloud Console
   - Add authorized domains
   - Copy Client ID/Secret to Render env vars

3. **Update Frontend:**
   - Verify `VITE_API_URL` points to deployed API
   - Test login flow
   - Verify CORS working

4. **Test Full Flow:**
   - Sign up with Google
   - Create a lead
   - View pipeline
   - Check activities
