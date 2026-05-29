#!/bin/bash
echo "╔══════════════════════════════════════════════╗"
echo "║       تشغيل دراستي الذكية                    ║"
echo "║       Starting Study AI App                   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# تشغيل الخادم الخلفي في الخلفية
echo "[1/2] تشغيل الخادم..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# انتظار
sleep 3

# تشغيل الواجهة
echo "[2/2] فتح التطبيق..."
cd frontend
if [ -f "build/index.html" ]; then
    npx electron .
else
    echo "بناء الواجهة أولاً..."
    npm run build
    npx electron .
fi

# إيقاف الخادم عند الإغلاق
kill $BACKEND_PID 2>/dev/null
