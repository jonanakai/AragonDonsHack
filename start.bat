@echo off
echo Starting AI Image Telephone...
echo.

echo Starting Flask backend...
start "Flask Backend" cmd /k "python app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting React frontend...
cd frontend
start "React Frontend" cmd /k "npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul 