# SCD System - Système de Cohésion et Discipline

## 📋 Project Overview

A disciplinary point system for managing student conduct with real-time features, role-based access (Conscrits, Anciens, P3), and family (Fam's) organization.

---

## 🏗️ Architecture

### Frontend (React + Vite)
- **Location**: `/scd-system/frontend/`
- **Framework**: React 19 + React Router DOM
- **Build Tool**: Vite 6
- **Deployment**: Vercel
- **URL**: `https://scd-system.vercel.app` (example)

### Backend (FastAPI)
- **Location**: `/scd-system/backend/`
- **Framework**: FastAPI + Peewee ORM
- **Database**: SQLite (mounted on Fly.io volume)
- **Authentication**: JWT tokens
- **Deployment**: Fly.io
- **URL**: `https://scd-api-roslan.fly.dev`

---

## 📁 Project Structure

```
scd-system/
├── frontend/                    # React application
│   ├── src/
│   │   ├── api.js              # API client (all HTTP calls)
│   │   ├── App.jsx             # Main router
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   └── pages/
│   │       ├── LoginPage.jsx
│   │       ├── SetupPage.jsx           # First-time login setup
│   │       ├── DashboardConscrit.jsx   # Conscrit dashboard
│   │       ├── DashboardAncien.jsx     # Ancien/P3 dashboard
│   │       ├── LogInfractionPage.jsx   # Log infractions (Ancien only)
│   │       ├── ClassementPage.jsx      # Rankings
│   │       ├── SettingsPage.jsx        # NEW: Profile/Password settings
│   │       ├── ProfilePage.jsx
│   │       ├── ForgotPasswordPage.jsx
│   │       └── ResetPasswordPage.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py             # FastAPI app entry
│   │   ├── routers/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── conscrits.py    # Conscrit CRUD
│   │   │   ├── infractions.py  # Infraction logging
│   │   │   ├── classement.py   # Rankings
│   │   │   └── websocket.py    # Real-time notifications
│   │   ├── models/             # Peewee ORM models
│   │   │   ├── personne.py
│   │   │   ├── infraction.py
│   │   │   ├── zone.py
│   │   │   ├── log.py
│   │   │   └── notification.py
│   │   ├── services/           # Business logic
│   │   ├── utils/              # Utilities
│   │   └── schemas/schemas.py  # Pydantic schemas
│   ├── Dockerfile
│   ├── fly.toml                # Fly.io config
│   └── requirements.txt
│
├── .github/workflows/
│   └── deploy.yml              # GitHub Actions (BROKEN - billing issue)
│
└── push-and-deploy.sh          # Manual deployment script (npx not available)
```

---

## 🔧 API Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | Login with nom/email + password | No |
| POST | `/auth/refresh` | Refresh JWT token | Yes |
| PATCH | `/auth/password` | Change password (old + new) | Yes |
| PATCH | `/auth/profile` | **NEW**: Update profile (email, buque, numero_fams) | Yes |
| POST | `/auth/setup` | First-time setup (password, email, buque, etc.) | Yes |
| POST | `/auth/forgot` | Request password reset | No |
| POST | `/auth/reset` | Reset password with token | No |
| GET | `/auth/anciens-list` | List all Anciens for setup | Yes |

### Conscrits (`/conscrits`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/conscrits/` | List all conscrits | Ancien/P3 only |
| GET | `/conscrits/{id}` | Get conscrit profile | Yes |
| GET | `/conscrits/{id}/historique` | Get infraction history | Yes |
| GET | `/conscrits/{id}/restrictions` | Get active restrictions | Yes |
| GET | `/conscrits/{id}/fam` | Get family tree | Yes |
| GET | `/conscrits/{id}/notifications` | Get notifications | Yes |
| POST | `/conscrits/{id}/notification/lu` | Mark notification read | Yes |
| PATCH | `/conscrits/{id}/buque` | Update buque | Yes |
| PATCH | `/conscrits/{id}/pa2` | Update PA2 (parent) | Yes |
| PATCH | `/conscrits/{id}/numero_fams` | Update numero_fams | Yes |

### Infractions (`/infractions`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/infractions/` | Log new infraction | Ancien/P3 only |
| GET | `/infractions/types` | List infraction types | Yes |

### Classement (`/classement`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/classement/individuel` | Individual rankings | Yes |
| GET | `/classement/fams` | Family rankings | Yes |
| GET | `/classement/stats` | Global statistics | Yes |

---

## 🚀 Deployment Configuration

### Frontend (Vercel)

**Build Settings:**
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Root Directory: `frontend`

**Environment Variables:**
```env
VITE_API_URL=https://scd-api-roslan.fly.dev
```

**Current API Base (hardcoded in `api.js`):**
```javascript
const API_BASE = 'https://scd-api-roslan.fly.dev';
```

### Backend (Fly.io)

**App Name**: `scd-api-roslan`

**fly.toml:**
```toml
app = "scd-api-roslan"
primary_region = "cdg"

[build]
  dockerfile = "Dockerfile"

[env]
  SCD_DATABASE_PATH = "/data/scd.db"
  SCD_RODAGE_ACTIF = "true"

[mounts]
  source = "scd_data"
  destination = "/data"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[services]]
  internal_port = 8000
  protocol = "tcp"
  [[services.ports]]
    handlers = ["http"]
    port = 80
  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SCD_DATABASE_PATH=/data/scd.db
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ⚠️ CURRENT PROBLEMS & SOLUTIONS

### Problem 1: GitHub Actions Deployment Failing

**Status**: ❌ BROKEN
**Error**: `The job was not started because your account is locked due to a billing issue.`

**Cause**: GitHub Actions minutes exceeded or billing issue

**Workaround**: Manual deployment via Vercel dashboard
1. Go to https://vercel.com/dashboard
2. Find project "scd-system"
3. Go to "Deployments" tab
4. Find latest commit
5. Click "Redeploy"

---

### Problem 2: npx Not Available Locally

**Status**: ❌ BROKEN
**Error**: `npx: command not found`

**Cause**: npm/npx not installed on development machine

**Workaround**: Use Vercel dashboard for deployment

---

### Problem 3: CORS Issues (RESOLVED)

**Status**: ✅ FIXED
**Error**: `CORS Missing Allow Origin` in browser

**Solution**: Backend CORS configured in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Problem 4: Backend Not Listening (RESOLVED)

**Status**: ✅ FIXED
**Error**: `WARNING The app is not listening on the expected address`

**Solution**: Added explicit `[[services]]` section to `fly.toml`

---

## 🔐 Authentication Flow

1. User logs in via `/auth/login`
2. Backend returns JWT token + user data
3. Frontend stores token in `localStorage` (key: `scd_token`)
4. Frontend stores user in `localStorage` (key: `scd_user`)
5. All API calls include `Authorization: Bearer <token>` header
6. On 401 error, user is redirected to `/login`

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| `CONSCRIT` | View own profile, history, restrictions, family tree |
| `ANCIEN` | Log infractions, view all conscrits, rankings |
| `P3` | Same as ANCIEN + admin privileges |

---

## 📝 Recent Changes (Latest Commit: 4630dd7)

### Added Settings Page
- **File**: `frontend/src/pages/SettingsPage.jsx`
- **Features**:
  - Edit email, buque, numero_fams
  - Change password (with confirmation)
  - Logout button
- **API Endpoint**: `PATCH /auth/profile`
- **Route**: `/settings`

### Backend Changes
- Added `ProfileUpdateRequest` schema in `auth.py`
- Added `PATCH /auth/profile` endpoint
- Validates email uniqueness
- Validates buque uniqueness

### Frontend Changes
- Added Settings button to DashboardConscrit header
- Added Settings button to DashboardAncien header
- Added `/settings` route in App.jsx

---

## 🧪 Testing Credentials

### Test Conscrit
- **Username**: `smani`
- **Password**: `smani225`
- **Name**: SMANI Ayoub
- **ID**: 52

### Test Database Reset
```bash
cd /scd-system/backend
python scripts/recreate_conscrits.py
```

---

## 🛠️ Common Commands

### Backend
```bash
# Deploy backend
cd backend
fly deploy

# Check backend status
curl https://scd-api-roslan.fly.dev/

# Check conscrits endpoint (should return 401 without token)
curl https://scd-api-roslan.fly.dev/conscrits/

# Login test
curl -X POST https://scd-api-roslan.fly.dev/auth/login \
  -H "Content-Type: application/json" \
  -d '{"nom":"smani","password":"smani225"}'
```

### Frontend
```bash
# Local development
cd frontend
npm run dev

# Build locally
npm run build

# Deploy (requires npx - NOT AVAILABLE CURRENTLY)
npx vercel --prod
```

### Git
```bash
# Push to GitHub
git add -A
git commit -m "your message"
git push origin main
```

---

## 🐛 Troubleshooting Guide

### "NetworkError when attempting to fetch resource"
1. Check backend is running: `curl https://scd-api-roslan.fly.dev/`
2. Check API_BASE in `api.js` matches backend URL
3. Check browser DevTools → Network for CORS errors

### "Impossible de charger les données" (Dashboard Ancien)
1. Backend endpoint `/conscrits/` requires authentication
2. Check user has valid token in localStorage
3. Check user role is ANCIEN or P3

### "Not Found" errors
1. Backend routes don't include `/api` prefix
2. API_BASE should be `https://scd-api-roslan.fly.dev` NOT `https://scd-api-roslan.fly.dev/api`

### Frontend shows old version
1. Clear browser cache (Ctrl+Shift+R)
2. Check Vercel dashboard for latest deployment
3. Verify commit hash matches latest push

---

## 📊 Database Schema (Key Tables)

### Personne (Users)
- id, nom, prenom, email, buque, numero_fams
- role (CONSCRIT/ANCIEN/P3)
- points_actuels, zone
- parent_id (PA2 reference)
- password_hash, first_login

### Infraction
- id, conscrit_id, type_infraction_id
- points, description, created_by

### Zone
- id, nom, seuil_min, seuil_max

### Log
- id, conscrit_id, type, message, created_at

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| Frontend (Vercel) | https://scd-system.vercel.app |
| Backend (Fly.io) | https://scd-api-roslan.fly.dev |
| Fly.io Dashboard | https://fly.io/apps/scd-api-roslan |
| Vercel Dashboard | https://vercel.com/dashboard |
| GitHub Repo | https://github.com/roslane07/scd-system |

---

## 🎯 Next Steps for New AI

1. **Check Current State**: Verify `git status` and last commit
2. **Backend Health**: Test `curl https://scd-api-roslan.fly.dev/`
3. **Frontend Deployment**: Check Vercel dashboard for latest deployment
4. **Test Login**: Try smani/smani225 credentials
5. **Feature Request**: User wants to modify profile after first login (already implemented in SettingsPage.jsx but may need deployment)

---

## 📞 Last Known Good State

- Backend: ✅ Working (responds to curl)
- GitHub Push: ✅ Working (commit 4630dd7 pushed)
- Vercel Deployment: ❌ Requires manual redeploy (GitHub Actions broken)
- Frontend Features: Settings page created but needs deployment
