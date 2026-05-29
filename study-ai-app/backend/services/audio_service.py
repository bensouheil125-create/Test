"""خدمة توليد الملخصات الصوتية بالعربية"""
import os
from gtts import gTTS


def generate_audio_summary(text, output_path, lang='ar'):
    """توليد ملخص صوتي من النص بالعربية الفصحى"""
    try:
        # تقسيم النص إذا كان طويلاً جداً
        max_chars = 5000
        if len(text) > max_chars:
            text = text[:max_chars]

        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)

        return {
            'نجاح': True,
            'مسار_الملف': output_path,
            'حجم_النص': len(text)
        }
    except Exception as e:
        return {
            'نجاح': False,
            'خطأ': str(e)
        }


def generate_chapter_audio(chapters, output_dir):
    """توليد ملفات صوتية لكل فصل"""
    results = []
    for i, chapter in enumerate(chapters):
        output_path = os.path.join(output_dir, f'chapter_{i + 1}.mp3')
        result = generate_audio_summary(chapter, output_path)
        result['رقم_الفصل'] = i + 1
        results.append(result)
    return results
