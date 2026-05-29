@echo off
chcp 65001 >nul
title بناء APK - دراستي الذكية
echo ╔══════════════════════════════════════════════════════════╗
echo ║    📱 بناء تطبيق دراستي الذكية - Android APK           ║
echo ║    Build Study AI App for Android                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: التحقق من Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js غير مثبت! https://nodejs.org
    pause
    exit /b 1
)

:: التحقق من Java
where java >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Java غير مثبت! مطلوب JDK 17+
    echo    https://adoptium.net/
)

cd frontend

echo [1/5] تثبيت المكتبات...
call npm install --legacy-peer-deps

echo.
echo [2/5] بناء الواجهة...
call npm run build

echo.
echo [3/5] تهيئة Capacitor...
call npm install @capacitor/core @capacitor/cli @capacitor/android --save 2>nul

echo.
echo [4/5] إضافة منصة Android...
call npx cap add android 2>nul

echo.
echo [5/5] نسخ الملفات...
call npx cap copy android
call npx cap sync android

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  ✅ تم التجهيز بنجاح!                                   ║
echo ║                                                          ║
echo ║  لبناء APK:                                              ║
echo ║  1. افتح Android Studio:  npx cap open android          ║
echo ║  2. أو من سطر الأوامر:                                   ║
echo ║     cd frontend\android                                  ║
echo ║     gradlew.bat assembleDebug                            ║
echo ║                                                          ║
echo ║  ملف APK:                                                ║
echo ║  android\app\build\outputs\apk\debug\app-debug.apk      ║
echo ╚══════════════════════════════════════════════════════════╝
cd ..
pause
