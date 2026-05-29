@echo off
chcp 65001 >nul
title دراستي الذكية - التثبيت السريع
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║          📚 دراستي الذكية - التثبيت السريع              ║
echo ║          Study AI - Quick Installer                      ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo هذا المثبت سيقوم بـ:
echo   1. التحقق من المتطلبات (Node.js + Python)
echo   2. تثبيت المكتبات المطلوبة تلقائياً
echo   3. بناء التطبيق
echo   4. إنشاء اختصار على سطح المكتب
echo.
echo ══════════════════════════════════════════════════════════
pause

:: التحقق من Node.js
echo.
echo [✓] التحقق من Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Node.js غير مثبت!
    echo    قم بتثبيته من: https://nodejs.org/en/download
    echo    اختر LTS version ثم أعد تشغيل هذا الملف
    echo.
    start https://nodejs.org/en/download
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do echo    Node.js %%v ✓

:: التحقق من Python
echo [✓] التحقق من Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Python غير مثبت!
    echo    قم بتثبيته من: https://www.python.org/downloads/
    echo    ⚠️ تأكد من اختيار "Add Python to PATH" عند التثبيت
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo    %%v ✓

echo.
echo ══════════════════════════════════════════════════════════
echo [1/4] تثبيت مكتبات Python...
echo ══════════════════════════════════════════════════════════
cd backend
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ❌ فشل تثبيت مكتبات Python
    pause
    exit /b 1
)
echo ✅ تم تثبيت مكتبات Python
cd ..

echo.
echo ══════════════════════════════════════════════════════════
echo [2/4] تثبيت مكتبات Node.js...
echo ══════════════════════════════════════════════════════════
cd frontend
call npm install --legacy-peer-deps
if %errorlevel% neq 0 (
    echo ❌ فشل تثبيت مكتبات Node.js
    pause
    exit /b 1
)
echo ✅ تم تثبيت مكتبات Node.js

echo.
echo ══════════════════════════════════════════════════════════
echo [3/4] بناء الواجهة الأمامية...
echo ══════════════════════════════════════════════════════════
call npm run build
if %errorlevel% neq 0 (
    echo ❌ فشل بناء الواجهة
    pause
    exit /b 1
)
echo ✅ تم بناء الواجهة بنجاح
cd ..

echo.
echo ══════════════════════════════════════════════════════════
echo [4/4] إنشاء اختصار على سطح المكتب...
echo ══════════════════════════════════════════════════════════

:: إنشاء ملف تشغيل بسيط
set "SCRIPT_DIR=%~dp0"
(
echo @echo off
echo chcp 65001 ^>nul
echo title دراستي الذكية
echo cd /d "%SCRIPT_DIR%backend"
echo start /min python app.py
echo timeout /t 2 /nobreak ^>nul
echo cd /d "%SCRIPT_DIR%frontend"
echo npx electron .
) > "%SCRIPT_DIR%دراستي_الذكية.bat"

:: إنشاء اختصار سطح المكتب
set "DESKTOP=%USERPROFILE%\Desktop"
(
echo [InternetShortcut]
echo URL=%SCRIPT_DIR%دراستي_الذكية.bat
echo IconIndex=0
) > "%DESKTOP%\دراستي الذكية.url"

echo ✅ تم إنشاء اختصار "دراستي الذكية" على سطح المكتب

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║   ✅ تم التثبيت بنجاح!                                  ║
echo ║                                                          ║
echo ║   لتشغيل التطبيق:                                       ║
echo ║   • انقر على "دراستي_الذكية.bat" في المجلد              ║
echo ║   • أو على الاختصار على سطح المكتب                      ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo هل تريد تشغيل التطبيق الآن؟ (Y/N)
set /p choice="> "
if /i "%choice%"=="Y" (
    call "%SCRIPT_DIR%دراستي_الذكية.bat"
)
