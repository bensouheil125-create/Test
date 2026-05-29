"""التطبيق الرئيسي - منصة دراستي الذكية"""
import os
import uuid
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from services.pdf_service import extract_text_from_pdf, get_pdf_info, split_text_into_chunks
from services.summary_service import (
    generate_summary, generate_key_points,
    generate_flashcards, generate_quiz,
    generate_presentation_content
)
from services.ai_service import (
    set_api_key, get_api_keys, is_ai_available,
    ai_summarize, ai_generate_key_points,
    ai_generate_flashcards, ai_generate_quiz,
    ai_generate_presentation
)
from services.audio_service import generate_audio_summary
from services.video_service import generate_video_from_text
from services.infographic_service import create_infographic

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)
CORS(app)

# تخزين مؤقت للنصوص المستخرجة
extracted_texts = {}


def allowed_file(filename):
    """التحقق من نوع الملف"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ===== واجهات API للذكاء الاصطناعي =====

@app.route('/api/settings/api-key', methods=['POST'])
def set_api_key_route():
    """تعيين مفتاح API للذكاء الاصطناعي"""
    data = request.get_json()
    provider = data.get('provider', 'openai')
    key = data.get('key', '')

    if not key:
        return jsonify({'خطأ': 'مفتاح API مطلوب'}), 400

    if provider not in ('openai', 'gemini'):
        return jsonify({'خطأ': 'المزود غير مدعوم. استخدم openai أو gemini'}), 400

    set_api_key(provider, key)
    return jsonify({
        'نجاح': True,
        'رسالة': f'تم تعيين مفتاح {provider.upper()} بنجاح',
        'المزود_النشط': provider
    })


@app.route('/api/settings/api-key', methods=['GET'])
def get_api_key_status():
    """الحصول على حالة مفاتيح API"""
    return jsonify(get_api_keys())


# ===== واجهات API الأساسية =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص صحة التطبيق"""
    return jsonify({
        'حالة': 'يعمل',
        'رسالة': 'منصة دراستي الذكية تعمل بنجاح',
        'الذكاء_الاصطناعي': is_ai_available()
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """رفع ملف PDF أو نصي"""
    if 'file' not in request.files:
        return jsonify({'خطأ': 'لم يتم إرسال ملف'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'خطأ': 'لم يتم اختيار ملف'}), 400

    if not allowed_file(file.filename):
        return jsonify({'خطأ': 'نوع الملف غير مدعوم. الأنواع المدعومة: PDF, TXT, DOCX'}), 400

    # حفظ الملف
    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    saved_filename = f"{file_id}.{file_ext}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, saved_filename)
    file.save(file_path)

    # استخراج النص
    try:
        if file_ext == 'pdf':
            text = extract_text_from_pdf(file_path)
            info = get_pdf_info(file_path)
        elif file_ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            info = {'عدد_الصفحات': 1, 'المؤلف': 'غير محدد', 'العنوان': filename}
        else:
            text = ""
            info = {'عدد_الصفحات': 0, 'المؤلف': 'غير محدد', 'العنوان': filename}

        # تخزين النص
        extracted_texts[file_id] = {
            'text': text,
            'filename': filename,
            'info': info
        }

        return jsonify({
            'نجاح': True,
            'معرف_الملف': file_id,
            'اسم_الملف': filename,
            'معلومات': info,
            'طول_النص': len(text),
            'معاينة': text[:500],
            'الذكاء_الاصطناعي_متاح': is_ai_available()
        })
    except Exception as e:
        return jsonify({'خطأ': str(e)}), 500


@app.route('/api/summary/<file_id>', methods=['GET'])
def get_summary(file_id):
    """الحصول على ملخص النص"""
    if file_id not in extracted_texts:
        return jsonify({'خطأ': 'الملف غير موجود'}), 404

    text = extracted_texts[file_id]['text']

    # محاولة استخدام الذكاء الاصطناعي أولاً
    ai_summary = None
    ai_points = None
    if is_ai_available():
        ai_summary = ai_summarize(text)
        ai_points = ai_generate_key_points(text)

    summary = ai_summary if ai_summary else generate_summary(text)
    key_points = ai_points if ai_points else generate_key_points(text)

    return jsonify({
        'نجاح': True,
        'ملخص': summary,
        'النقاط_الرئيسية': key_points,
        'اسم_الملف': extracted_texts[file_id]['filename'],
        'بالذكاء_الاصطناعي': bool(ai_summary)
    })


@app.route('/api/audio/<file_id>', methods=['GET'])
def get_audio_summary(file_id):
    """توليد ملخص صوتي"""
    if file_id not in extracted_texts:
        return jsonify({'خطأ': 'الملف غير موجود'}), 404

    text = extracted_texts[file_id]['text']

    # استخدام AI للتلخيص إن أمكن
    if is_ai_available():
        summary = ai_summarize(text)
        if not summary:
            summary = generate_summary(text, max_sentences=8)
    else:
        summary = generate_summary(text, max_sentences=8)

    output_dir = os.path.join(Config.OUTPUT_FOLDER, file_id)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'audio_summary.mp3')

    result = generate_audio_summary(summary, output_path)

    if result['نجاح']:
        return send_file(output_path, mimetype='audio/mpeg', as_attachment=True,
                         download_name='ملخص_صوتي.mp3')
    else:
        return jsonify({'خطأ': result['خطأ']}), 500


@app.route('/api/video/<file_id>', methods=['GET'])
def get_video(file_id):
    """توليد فيديو تعليمي"""
    if file_id not in extracted_texts:
        return jsonify({'خطأ': 'الملف غير موجود'}), 404

    text = extracted_texts[file_id]['text']
    title = extracted_texts[file_id].get('filename', 'ملخص الكتاب')

    if is_ai_available():
        summary = ai_summarize(text)
        if not summary:
            summary = generate_summary(text, max_sentences=12)
    else:
        summary = generate_summary(text, max_sentences=12)

    output_dir = os.path.join(Config.OUTPUT_FOLDER, file_id)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'video_summary.mp4')

    result = generate_video_from_text(summary, output_path, title=title)

    if result.get('نجاح'):
        if os.path.exists(output_path):
            return send_file(output_path, mimetype='video/mp4', as_attachment=True,
                             download_name='فيديو_تعليمي.mp4')
        elif 'مسار_الصوت' in result:
            return send_file(result['مسار_الصوت'], mimetype='audio/mpeg', as_attachment=True,
                             download_name='ملخص_صوتي.mp3')

    return jsonify(result), 500 if not result.get('نجاح') else 200


@app.route('/api/flashcards/<file_id>', methods=['GET'])
def get_flashcards(file_id):
    """توليد بطاقات تعليمية"""
    if file_id not in extracted_texts:
        return jsonify({'خطأ': 'الملف غير موجود'}), 404

    text = extracted_texts[file_id]['text']
    num_cards = request.args.get('num', 10, type=int)

    # محاولة استخدام AI
    cards = None
    if is_ai_available():
        cards = ai_generate_flashcards(text, num_cards=num_cards)

    if not cards:
        cards = generate_flashcards(text, num_cards=num_cards)

    return jsonify({
        'نجاح': True,
        'بطاقات': cards,
        'العدد': len(cards),
        'بالذكاء_الاصطناعي': is_ai_available() and cards is not None
    })


@app.route('/api/quiz/<file_id>', methods=['GET'])
def get_quiz(file_id):
    """توليد اختبار"""
    if file_id not in extracted_texts:
        return jsonify({'خطأ': 'الملف غير موجود'}), 404

    text = extracted_texts[file_id]['text']
    num_questions = request.args.get('num', 5, type=int)

    # محاولة استخدام AI
    quiz = None
    if is_ai_available():
        quiz = ai_generate_quiz(text, num_questions=num_questions)

    if not quiz:
        quiz = generate_quiz(text, num_questions=num_questions)

    return jsonify({
        'نجاح': True,
        'اختبار': quiz,
        'عدد_الأسئلة': len(quiz),
        'بالذكاء_الاصطناعي': is_ai_available() and quiz is not None
    })


@app.route('/api/presentation/<file_id>', methods=['GET'])
def get_presentation(file_id):
    """توليد محتوى عرض تقديمي"""
    if file_id not in extracted_texts:
        return jsonify({'خطأ': 'الملف غير موجود'}), 404

    text = extracted_texts[file_id]['text']

    # محاولة استخدام AI
    slides = None
    if is_ai_available():
        slides = ai_generate_presentation(text)

    if not slides:
        slides = generate_presentation_content(text)

    return jsonify({
        'نجاح': True,
        'شرائح': slides,
        'عدد_الشرائح': len(slides),
        'بالذكاء_الاصطناعي': is_ai_available() and slides is not None
    })


@app.route('/api/infographic/<file_id>', methods=['GET'])
def get_infographic(file_id):
    """توليد إنفوغرافيك"""
    if file_id not in extracted_texts:
        return jsonify({'خطأ': 'الملف غير موجود'}), 404

    text = extracted_texts[file_id]['text']
    title = extracted_texts[file_id].get('filename', 'ملخص')

    # محاولة استخدام AI للنقاط
    key_points = None
    if is_ai_available():
        key_points = ai_generate_key_points(text)

    if not key_points:
        key_points = generate_key_points(text, max_points=8)

    output_dir = os.path.join(Config.OUTPUT_FOLDER, file_id)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'infographic.png')

    result = create_infographic(title, key_points, output_path)

    if result['نجاح']:
        return send_file(output_path, mimetype='image/png', as_attachment=True,
                         download_name='إنفوغرافيك.png')

    return jsonify({'خطأ': 'فشل في إنشاء الإنفوغرافيك'}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    """عرض قائمة الملفات المرفوعة"""
    files = []
    for file_id, data in extracted_texts.items():
        files.append({
            'معرف': file_id,
            'اسم_الملف': data['filename'],
            'معلومات': data['info'],
            'طول_النص': len(data['text'])
        })
    return jsonify({'ملفات': files})


@app.route('/api/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """حذف ملف"""
    if file_id in extracted_texts:
        del extracted_texts[file_id]
        return jsonify({'نجاح': True, 'رسالة': 'تم حذف الملف بنجاح'})
    return jsonify({'خطأ': 'الملف غير موجود'}), 404


if __name__ == '__main__':
    print("=" * 50)
    print("  منصة دراستي الذكية")
    print("  Arabic Study AI Platform")
    print("=" * 50)
    print(f"  الخادم يعمل على: http://localhost:5000")
    print(f"  الذكاء الاصطناعي: {'متاح' if is_ai_available() else 'غير مفعل - أضف مفتاح API'}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
