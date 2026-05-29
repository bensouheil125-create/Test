@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════╗
echo ║       تشغيل دراستي الذكية                    ║
echo ║       Starting Study AI App                   ║
echo ╚══════════════════════════════════════════════╝
echo.

:: تشغيل الخادم الخلفي
echo [1/2] تشغيل الخادم...
start /min cmd /c "cd backend && python app.py"

:: انتظار 3 ثوان
timeout /t 3 /nobreak >nul

:: تشغيل الواجهة
echo [2/2] فتح التطبيق...
cd frontend
if exist "build\index.html" (
    npx electron .
) else (
    echo بناء الواجهة أولاً...
    call npm run build
    npx electron .
)
