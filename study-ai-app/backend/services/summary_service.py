"""خدمة التلخيص وتوليد المحتوى التعليمي (بدون AI كخيار احتياطي)"""
import re


def generate_summary(text, max_sentences=10):
    """توليد ملخص من النص"""
    sentences = re.split(r'[.。!؟!\n]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return "لا يمكن توليد ملخص من هذا النص"

    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0
        if i < 5:
            score += 3
        if 30 < len(sentence) < 200:
            score += 2
        important_words = ['يعتبر', 'أهم', 'الأساسي', 'يجب', 'النتيجة', 'الخلاصة',
                          'أولاً', 'ثانياً', 'أخيراً', 'بالإضافة', 'من ناحية', 'لذلك']
        for word in important_words:
            if word in sentence:
                score += 1
        scored_sentences.append((score, i, sentence))

    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    selected = scored_sentences[:max_sentences]
    selected.sort(key=lambda x: x[1])

    summary = '. '.join([s[2] for s in selected])
    return summary


def generate_key_points(text, max_points=8):
    """استخراج النقاط الرئيسية"""
    sentences = re.split(r'[.。!؟!\n]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    key_points = []
    for sentence in sentences[:50]:
        if any(word in sentence for word in ['هو', 'هي', 'يعني', 'تعريف', 'أن', 'يتضمن', 'يعتبر']):
            if len(sentence) < 150:
                key_points.append(sentence)
        if len(key_points) >= max_points:
            break

    if len(key_points) < 3:
        step = max(1, len(sentences) // max_points)
        key_points = [sentences[i] for i in range(0, min(len(sentences), max_points * step), step)][:max_points]

    return key_points


def generate_flashcards(text, num_cards=10):
    """توليد بطاقات تعليمية"""
    sentences = re.split(r'[.。!؟!\n]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    flashcards = []
    for i, sentence in enumerate(sentences[:num_cards * 2]):
        if len(flashcards) >= num_cards:
            break

        if 'هو' in sentence or 'هي' in sentence:
            parts = sentence.split('هو' if 'هو' in sentence else 'هي', 1)
            if len(parts) == 2 and len(parts[0].strip()) > 5:
                question = f"ما {'هو' if 'هو' in sentence else 'هي'} {parts[0].strip()}؟"
                answer = parts[1].strip()
                flashcards.append({'سؤال': question, 'جواب': answer})
        elif 'يعني' in sentence:
            parts = sentence.split('يعني', 1)
            if len(parts) == 2:
                question = f"ماذا يعني {parts[0].strip()}؟"
                answer = parts[1].strip()
                flashcards.append({'سؤال': question, 'جواب': answer})
        else:
            question = f"اشرح: {sentence[:60]}...؟"
            answer = sentence
            flashcards.append({'سؤال': question, 'جواب': answer})

    return flashcards


def generate_quiz(text, num_questions=5):
    """توليد اختبار من النص"""
    sentences = re.split(r'[.。!؟!\n]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    quiz = []
    used_indices = set()

    for i in range(0, min(len(sentences), num_questions * 3), 3):
        if len(quiz) >= num_questions:
            break
        if i in used_indices:
            continue

        sentence = sentences[i]
        question = {
            'سؤال': f"هل العبارة التالية صحيحة: \"{sentence[:80]}\"؟",
            'الخيارات': ['صحيح', 'خطأ', 'غير مذكور في النص', 'يحتاج توضيح'],
            'الإجابة_الصحيحة': 'صحيح',
            'شرح': sentence
        }
        quiz.append(question)
        used_indices.add(i)

    return quiz[:num_questions]


def generate_presentation_content(text, num_slides=8):
    """توليد محتوى عرض تقديمي"""
    summary = generate_summary(text, max_sentences=15)
    key_points = generate_key_points(text, max_points=12)

    slides = []

    slides.append({
        'عنوان': 'ملخص المحتوى',
        'محتوى': 'عرض تقديمي تم إنشاؤه تلقائياً من الكتاب',
        'نوع': 'عنوان'
    })

    slides.append({
        'عنوان': 'نظرة عامة',
        'محتوى': summary[:200],
        'نوع': 'نص'
    })

    points_per_slide = 3
    for i in range(0, len(key_points), points_per_slide):
        slide_points = key_points[i:i + points_per_slide]
        slides.append({
            'عنوان': f'النقاط الرئيسية ({i // points_per_slide + 1})',
            'محتوى': slide_points,
            'نوع': 'نقاط'
        })

    slides.append({
        'عنوان': 'الخلاصة',
        'محتوى': summary[:150],
        'نوع': 'نص'
    })

    return slides[:num_slides]
