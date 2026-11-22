@echo off
title AICTE NEXUS - Platform Launcher
echo =====================================================================
echo  AICTE NEXUS - Launching Complete Platform (Backend + Frontend)
echo =====================================================================
start "AICTE NEXUS Backend" cmd /c "D:\sih_problm1.0\start-backend.bat"
timeout /t 3 /nobreak >nul
start "AICTE NEXUS Frontend" cmd /c "D:\sih_problm1.0\start-frontend.bat"
echo.
echo Both servers launched in separate console windows.
echo Frontend: http://localhost:3000
echo Backend API Docs: http://localhost:8000/docs
echo =====================================================================
pause
