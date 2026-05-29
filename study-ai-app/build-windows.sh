#!/bin/bash
echo "╔══════════════════════════════════════════════╗"
echo "║    بناء تطبيق دراستي الذكية - Windows       ║"
echo "║    Build Study AI App for Windows (Wine)     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# التحقق من المتطلبات
command -v node >/dev/null 2>&1 || { echo "❌ Node.js مطلوب"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 مطلوب"; exit 1; }

echo "[1/4] تثبيت مكتبات Python..."
cd backend
pip3 install -r requirements.txt
cd ..

echo ""
echo "[2/4] تثبيت مكتبات Node.js..."
cd frontend
npm install

echo ""
echo "[3/4] بناء الواجهة الأمامية..."
npm run build

echo ""
echo "[4/4] بناء ملف التثبيت..."
npx electron-builder --win

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ✅ تم البناء بنجاح!                        ║"
echo "║  الملف في: frontend/dist/                   ║"
echo "╚══════════════════════════════════════════════╝"
cd ..
