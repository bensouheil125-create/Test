@echo off
echo ========================================
echo   PS Multi Timer - Build EXE
echo ========================================
echo.

:: Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found! 
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
call npm install

echo.
echo [2/3] Building portable EXE...
call npm run build-portable

echo.
echo [3/3] Done!
echo.
echo Your EXE file is in the "dist" folder:
echo   dist\PS-Multi-Timer.exe
echo.
echo This file works on Windows 10 and 11 without installation.
pause