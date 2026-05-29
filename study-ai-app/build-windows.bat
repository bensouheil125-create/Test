@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════╗
echo ║    بناء تطبيق دراستي الذكية - Windows       ║
echo ║    Build Study AI App for Windows            ║
echo ╚══════════════════════════════════════════════╝
echo.

:: التحقق من Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js غير مثبت! قم بتثبيته من: https://nodejs.org
    pause
    exit /b 1
)

:: التحقق من Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python غير مثبت! قم بتثبيته من: https://python.org
    pause
    exit /b 1
)

echo [1/4] تثبيت مكتبات Python...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo [2/4] تثبيت مكتبات Node.js...
cd frontend
call npm install

echo.
echo [3/4] بناء الواجهة الأمامية...
call npm run build

echo.
echo [4/4] بناء ملف التثبيت EXE...
call npx electron-builder --win

echo.
echo ╔══════════════════════════════════════════════╗
echo ║  ✅ تم البناء بنجاح!                        ║
echo ║  الملف موجود في: frontend\dist\             ║
echo ╚══════════════════════════════════════════════╝
echo.
cd ..
pause
