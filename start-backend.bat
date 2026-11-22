@echo off
title AICTE NEXUS - FastAPI Backend Server
echo =====================================================================
echo  AICTE NEXUS - Intelligent Institution Complaint Monitoring Platform
echo  Starting FastAPI Backend on http://localhost:8000
echo =====================================================================
set TMP=D:\temp
set TEMP=D:\temp
cd /d D:\sih_problm1.0\backend
call .\venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
