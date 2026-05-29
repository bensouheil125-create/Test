# 📚 دراستي الذكية - Study AI

منصة تعليمية ذكية بالعربية الفصحى تقوم بتحليل الكتب وملفات PDF وتحويلها إلى محتوى تعليمي متنوع.

## ✨ المميزات

- 🎙️ **ملخص صوتي** - استمع لملخص الكتاب بالعربية الفصحى
- 🎬 **ملخص فيديو** - فيديو تعليمي يشرح المحتوى
- 🖥️ **عرض تقديمي** - شرائح عرض من محتوى الكتاب
- 🗂️ **بطاقات تعليمية** - بطاقات سؤال وجواب للمراجعة
- ❓ **اختبار** - اختبر فهمك للمحتوى
- 📊 **إنفوغرافيك** - رسم بياني يلخص المعلومات
- 🤖 **ذكاء اصطناعي** - دعم OpenAI و Google Gemini

## 🚀 التشغيل

### المتطلبات
- Python 3.9+
- Node.js 18+
- ffmpeg (اختياري - للفيديو)

### تشغيل الخادم (Backend)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

الخادم سيعمل على: http://localhost:5000

### تشغيل الواجهة (Frontend)

```bash
cd frontend
npm install
npm start
```

الواجهة ستعمل على: http://localhost:3000

## 🔑 إعداد الذكاء الاصطناعي

يمكنك إضافة مفتاح API من خلال:

### الطريقة 1: من واجهة التطبيق
1. افتح التطبيق
2. اذهب إلى ⚙️ الإعدادات
3. اختر المزود (OpenAI أو Gemini)
4. أدخل مفتاح API واحفظه

### الطريقة 2: متغيرات البيئة
```bash
export OPENAI_API_KEY=sk-...
# أو
export GEMINI_API_KEY=AIza...
```

> **ملاحظة:** التطبيق يعمل بدون مفتاح API بخوارزميات أساسية، ومع المفتاح يعطي نتائج أفضل بكثير.

## 📱 التشغيل على الأجهزة المختلفة

### Android (APK)
استخدم Capacitor لتحويل التطبيق إلى APK:
```bash
cd frontend
npm install @capacitor/core @capacitor/cli
npx cap init "دراستي الذكية" "com.studyai.app"
npx cap add android
npm run build
npx cap copy android
npx cap open android
```
ثم ابني APK من Android Studio.

### iOS
```bash
cd frontend
npx cap add ios
npm run build
npx cap copy ios
npx cap open ios
```
ثم ابني التطبيق من Xcode.

### Windows (7/8/10/11)
استخدم Electron لتشغيل التطبيق على Windows:
```bash
cd frontend
npm install electron electron-builder --save-dev
npm run build
npx electron .
```
أو استخدم ملف `electron-main.js` المرفق.

## 📂 هيكل المشروع

```
study-ai-app/
├── backend/
│   ├── app.py              # التطبيق الرئيسي Flask
│   ├── config.py           # الإعدادات
│   ├── requirements.txt    # المكتبات المطلوبة
│   ├── services/
│   │   ├── ai_service.py       # خدمة الذكاء الاصطناعي
│   │   ├── pdf_service.py      # استخراج النصوص
│   │   ├── summary_service.py  # التلخيص
│   │   ├── audio_service.py    # الملخص الصوتي
│   │   ├── video_service.py    # الفيديو التعليمي
│   │   └── infographic_service.py # الإنفوغرافيك
│   ├── uploads/            # الملفات المرفوعة
│   └── outputs/            # الملفات المولدة
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── pages/          # صفحات التطبيق
│   │   ├── components/     # المكونات
│   │   └── styles/         # الأنماط
│   ├── capacitor.config.ts # إعدادات الموبايل
│   └── electron-main.js   # إعدادات Windows
└── README.md
```

## 🛠️ التقنيات المستخدمة

| التقنية | الاستخدام |
|---------|----------|
| Flask | الخادم الخلفي |
| React | الواجهة الأمامية |
| gTTS | تحويل النص لصوت |
| Pillow | توليد الصور |
| ffmpeg | إنشاء الفيديو |
| OpenAI/Gemini | الذكاء الاصطناعي |
| Capacitor | تطبيق الموبايل |
| Electron | تطبيق Windows |

## 📝 الترخيص

MIT License
