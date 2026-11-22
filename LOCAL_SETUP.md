# AICTE NEXUS — Local Development Setup Guide

## 1. Environment Requirements

- **Operating System**: Windows 10/11 or Linux
- **Python**: 3.12.x or 3.13.x
- **Node.js**: v20+ / v22+ / v24+
- **PostgreSQL**: Local service running (Port `5433` or `5432`)
- **Redis**: Running locally on `localhost:6379`

---

## 2. Fast Launch Using Batch Scripts (Windows)

The repository provides automated startup scripts in the root directory:

1. **Launch Complete Platform**:
   Double click `start-all.bat` (or execute in PowerShell):
   ```powershell
   .\start-all.bat
   ```
   This opens both the FastAPI backend and Next.js frontend in separate terminal windows.

2. **Launch Backend Individually**:
   ```powershell
   .\start-backend.bat
   ```
   Runs at: `http://localhost:8000` (Swagger Docs: `http://localhost:8000/docs`)

3. **Launch Frontend Individually**:
   ```powershell
   .\start-frontend.bat
   ```
   Runs at: `http://localhost:3000`

---

## 3. Manual Step-by-Step Setup

### Step A: Backend Setup
```powershell
cd D:\sih_problm1.0\backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python bootstrap_admin.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step B: Frontend Setup
```powershell
cd D:\sih_problm1.0\frontend
npm install
npm run dev
```

---

## 4. Default Super Admin Credentials

- **Username**: `admin`
- **Password**: `AicteNexus@2026SecureAdmin`
- **Assigned Role**: Super Administrator (`ADMIN_FULL`)
- **Access Level**: Full access across all AICTE bureaus, sieve overlap review, and system configuration.
