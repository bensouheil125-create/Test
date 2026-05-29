# 📚 دراستي الذكية - دليل التثبيت والاستخدام

## 🖥️ التثبيت على Windows (7/8/10/11)

### الطريقة 1: التثبيت السريع (مستحسنة)

1. **ثبّت المتطلبات أولاً:**
   - [Node.js](https://nodejs.org/en/download) - اختر "LTS" ثم "Windows Installer"
   - [Python](https://www.python.org/downloads/) - ⚠️ عند التثبيت اختر ✅ "Add Python to PATH"

2. **حمّل المشروع** من GitHub:
   - اذهب إلى: https://github.com/bensouheil125-create/Test
   - اضغط على الزر الأخضر "Code" → "Download ZIP"
   - فك الضغط في أي مكان

3. **شغّل المثبت:**
   - افتح مجلد `study-ai-app`
   - انقر نقرتين على **`install-windows.bat`**
   - انتظر حتى ينتهي (5-10 دقائق أول مرة فقط)
   - سيُنشئ اختصاراً على سطح المكتب ✅

4. **التشغيل بعد ذلك:**
   - انقر على **`دراستي_الذكية.bat`** في المجلد
   - أو الاختصار على سطح المكتب

---

### الطريقة 2: بناء ملف EXE مستقل

هذا ينشئ ملف `.exe` يمكن نقله لأي جهاز Windows:

```batch
cd study-ai-app\frontend
npm run electron-build
```

ستجد الملف في: `frontend\dist\دراستي الذكية Setup.exe`

---

## 📱 التثبيت على Android (APK)

### الطريقة 1: بناء APK على حاسوبك

#### المتطلبات:
- [Android Studio](https://developer.android.com/studio) مثبت
- [Java JDK 17](https://adoptium.net/) مثبت
- [Node.js](https://nodejs.org) مثبت

#### الخطوات:

1. **حمّل المشروع** من GitHub وفك الضغط

2. **شغّل سكريبت البناء:**
   - **Windows:** انقر نقرتين على `build-android.bat`
   - **Mac/Linux:** `./build-android.sh`

3. **ابنِ ملف APK:**
   ```bash
   cd study-ai-app/frontend/android
   ./gradlew assembleDebug
   ```
   (على Windows: `gradlew.bat assembleDebug`)

4. **ملف APK جاهز في:**
   ```
   frontend/android/app/build/outputs/apk/debug/app-debug.apk
   ```

5. **انقل ملف APK** إلى هاتفك وثبته

#### أو من Android Studio:
```bash
cd study-ai-app/frontend
npx cap open android
```
ثم اضغط "Run" ▶️ في Android Studio

---

### ⚠️ ملاحظة مهمة عن تطبيق Android:

تطبيق Android يعرض **الواجهة الأمامية فقط**. لكي يعمل بالكامل تحتاج:

1. **تشغيل الخادم الخلفي** على حاسوبك:
   ```bash
   cd study-ai-app/backend
   python app.py
   ```

2. **تعديل عنوان الخادم** في التطبيق:
   - افتح `frontend/src/pages/UploadPage.js`
   - غيّر `http://localhost:5000` إلى `http://عنوان_IP_حاسوبك:5000`
   - مثال: `http://192.168.1.5:5000`
   - ⚠️ تأكد أن الهاتف والحاسوب على نفس شبكة WiFi

3. **أو استخدم خادم سحابي** (مثل Railway، Render، أو VPS)

---

## 🐧 التشغيل على Linux

```bash
cd study-ai-app

# تثبيت مكتبات Python
cd backend
pip3 install -r requirements.txt
cd ..

# تثبيت وبناء الواجهة
cd frontend
npm install
npm run build

# تشغيل التطبيق
./run-app.sh
```

---

## 🍎 التثبيت على iOS

يتطلب macOS + Xcode:

```bash
cd study-ai-app/frontend
npm install @capacitor/ios
npx cap add ios
npm run build
npx cap copy ios
npx cap open ios
```
ثم ابنِ التطبيق من Xcode.

---

## ⚙️ إعداد الذكاء الاصطناعي

التطبيق يعمل **بدون مفتاح AI** بخوارزميات أساسية.
لنتائج أفضل بكثير، أضف مفتاح API:

### من داخل التطبيق:
1. افتح التطبيق
2. اضغط ⚙️ (الإعدادات)
3. اختر المزود: **OpenAI** أو **Google Gemini**
4. أدخل المفتاح واحفظه

### الحصول على مفتاح:
- **OpenAI:** https://platform.openai.com/api-keys (مدفوع)
- **Google Gemini:** https://aistudio.google.com/apikey (مجاني)

---

## 🔧 حل المشاكل

| المشكلة | الحل |
|---------|------|
| "node not found" | ثبّت Node.js وأعد تشغيل الحاسوب |
| "python not found" | ثبّت Python مع خيار "Add to PATH" |
| التطبيق لا يتصل بالخادم | تأكد أن `python app.py` يعمل |
| فشل بناء APK | تأكد من تثبيت Android Studio + JDK 17 |
| ffmpeg not found | الفيديو سيُنشأ كملف صوتي. ثبّت ffmpeg لدعم الفيديو |

### تثبيت ffmpeg (اختياري - لدعم الفيديو):
- **Windows:** https://www.gyan.dev/ffmpeg/builds/ (حمّل essentials)
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

---

## 📋 ملخص الملفات المهمة

| الملف | الوظيفة |
|-------|---------|
| `install-windows.bat` | مثبت Windows السريع |
| `run-app.bat` | تشغيل التطبيق على Windows |
| `run-app.sh` | تشغيل التطبيق على Linux/Mac |
| `build-windows.bat` | بناء ملف EXE |
| `build-android.bat` | تجهيز مشروع Android |
| `build-android.sh` | تجهيز مشروع Android (Linux/Mac) |
| `backend/app.py` | الخادم الخلفي |
| `frontend/build/` | الواجهة المبنية جاهزة |
