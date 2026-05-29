#!/bin/bash
echo "╔══════════════════════════════════════════════════════════╗"
echo "║    📱 بناء تطبيق دراستي الذكية - Android APK           ║"
echo "║    Build Study AI App for Android                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# التحقق من المتطلبات
command -v node >/dev/null 2>&1 || { echo "❌ Node.js مطلوب. ثبته من: https://nodejs.org"; exit 1; }
command -v npx >/dev/null 2>&1 || { echo "❌ npx غير موجود"; exit 1; }

echo "المتطلبات:"
echo "  • Node.js ✓ ($(node --version))"
echo "  • Android Studio (مطلوب لبناء APK)"
echo "  • Java JDK 17+ (مطلوب لبناء APK)"
echo ""

cd frontend

echo "[1/5] تثبيت المكتبات..."
npm install --legacy-peer-deps

echo ""
echo "[2/5] بناء الواجهة الأمامية..."
npm run build

echo ""
echo "[3/5] تهيئة Capacitor..."
# تثبيت Capacitor إذا لم يكن مثبتاً
npm install @capacitor/core @capacitor/cli @capacitor/android --save 2>/dev/null

echo ""
echo "[4/5] إضافة منصة Android..."
npx cap add android 2>/dev/null || echo "   (المنصة موجودة مسبقاً)"

echo ""
echo "[5/5] نسخ الملفات إلى مشروع Android..."
npx cap copy android
npx cap sync android

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ تم التجهيز بنجاح!                                   ║"
echo "║                                                          ║"
echo "║  الخطوة التالية:                                         ║"
echo "║  1. افتح المشروع في Android Studio:                      ║"
echo "║     npx cap open android                                 ║"
echo "║                                                          ║"
echo "║  2. أو ابنِ APK مباشرة:                                  ║"
echo "║     cd frontend/android                                  ║"
echo "║     ./gradlew assembleDebug                              ║"
echo "║                                                          ║"
echo "║  3. ملف APK سيكون في:                                    ║"
echo "║     android/app/build/outputs/apk/debug/app-debug.apk   ║"
echo "╚══════════════════════════════════════════════════════════╝"

cd ..
