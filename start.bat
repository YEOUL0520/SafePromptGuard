@echo off
echo SafePrompt Guard 시작...
start "Backend" cmd /k "cd /d %~dp0backend && python -m venv venv 2>nul && call venv\Scripts\activate && pip install -r requirements.txt -q && uvicorn main:app --reload --port 8001"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"
echo.
echo Backend: http://localhost:8001
echo Frontend: http://localhost:5173
pause
