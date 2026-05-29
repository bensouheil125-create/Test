"""خدمة الذكاء الاصطناعي - دعم OpenAI و Gemini"""
import os

# متغير عام لتخزين مفاتيح API
_api_keys = {
    'openai': os.environ.get('OPENAI_API_KEY', ''),
    'gemini': os.environ.get('GEMINI_API_KEY', ''),
    'provider': 'openai'  # openai أو gemini
}


def set_api_key(provider, key):
    """تعيين مفتاح API"""
    _api_keys[provider] = key
    _api_keys['provider'] = provider


def get_api_keys():
    """الحصول على حالة مفاتيح API"""
    return {
        'openai_configured': bool(_api_keys.get('openai')),
        'gemini_configured': bool(_api_keys.get('gemini')),
        'active_provider': _api_keys.get('provider', 'openai')
    }


def is_ai_available():
    """التحقق من توفر خدمة الذكاء الاصطناعي"""
    provider = _api_keys.get('provider', 'openai')
    return bool(_api_keys.get(provider))


def ai_generate(prompt, system_prompt="أنت مساعد تعليمي ذكي. أجب دائماً بالعربية الفصحى."):
    """توليد نص باستخدام الذكاء الاصطناعي"""
    provider = _api_keys.get('provider', 'openai')

    if provider == 'openai' and _api_keys.get('openai'):
        return _openai_generate(prompt, system_prompt)
    elif provider == 'gemini' and _api_keys.get('gemini'):
        return _gemini_generate(prompt, system_prompt)
    else:
        return None


def _openai_generate(prompt, system_prompt):
    """توليد نص باستخدام OpenAI"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=_api_keys['openai'])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"خطأ OpenAI: {e}")
        return None


def _gemini_generate(prompt, system_prompt):
    """توليد نص باستخدام Google Gemini"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=_api_keys['gemini'])
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"خطأ Gemini: {e}")
        return None


def ai_summarize(text):
    """تلخيص النص بالذكاء الاصطناعي"""
    prompt = f"""قم بتلخيص النص التالي بالعربية الفصحى في فقرة واحدة شاملة ومفيدة:

{text[:4000]}"""
    return ai_generate(prompt)


def ai_generate_key_points(text):
    """استخراج النقاط الرئيسية بالذكاء الاصطناعي"""
    prompt = f"""استخرج أهم 8 نقاط رئيسية من النص التالي. اكتب كل نقطة في سطر منفصل بالعربية الفصحى.
ابدأ كل نقطة بـ "•"

النص:
{text[:4000]}"""
    result = ai_generate(prompt)
    if result:
        points = [line.strip().lstrip('•').strip() for line in result.split('\n') if line.strip() and line.strip() != '•']
        return points[:8]
    return None


def ai_generate_flashcards(text, num_cards=10):
    """توليد بطاقات تعليمية بالذكاء الاصطناعي"""
    prompt = f"""أنشئ {num_cards} بطاقات تعليمية (سؤال وجواب) من النص التالي بالعربية الفصحى.
استخدم التنسيق التالي لكل بطاقة:
سؤال: [السؤال هنا]
جواب: [الجواب هنا]
---

النص:
{text[:4000]}"""
    result = ai_generate(prompt)
    if result:
        cards = []
        current_q = ""
        current_a = ""
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('سؤال:'):
                if current_q and current_a:
                    cards.append({'سؤال': current_q, 'جواب': current_a})
                current_q = line.replace('سؤال:', '').strip()
                current_a = ""
            elif line.startswith('جواب:'):
                current_a = line.replace('جواب:', '').strip()
        if current_q and current_a:
            cards.append({'سؤال': current_q, 'جواب': current_a})
        return cards[:num_cards]
    return None


def ai_generate_quiz(text, num_questions=5):
    """توليد اختبار بالذكاء الاصطناعي"""
    prompt = f"""أنشئ اختبار من {num_questions} أسئلة اختيار من متعدد من النص التالي بالعربية الفصحى.
لكل سؤال قدم 4 خيارات وحدد الإجابة الصحيحة.
استخدم التنسيق التالي:
سؤال: [السؤال]
أ) [الخيار الأول]
ب) [الخيار الثاني]
ج) [الخيار الثالث]
د) [الخيار الرابع]
الإجابة: [حرف الإجابة الصحيحة]
شرح: [شرح مختصر]
---

النص:
{text[:4000]}"""
    result = ai_generate(prompt)
    if result:
        questions = []
        current = {}
        options = []
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('سؤال:'):
                if current.get('سؤال'):
                    current['الخيارات'] = options
                    questions.append(current)
                current = {'سؤال': line.replace('سؤال:', '').strip()}
                options = []
            elif line.startswith(('أ)', 'ب)', 'ج)', 'د)')):
                options.append(line[2:].strip())
            elif line.startswith('الإجابة:'):
                answer_letter = line.replace('الإجابة:', '').strip()
                letter_map = {'أ': 0, 'ب': 1, 'ج': 2, 'د': 3}
                idx = letter_map.get(answer_letter, 0)
                if idx < len(options):
                    current['الإجابة_الصحيحة'] = options[idx]
                elif options:
                    current['الإجابة_الصحيحة'] = options[0]
            elif line.startswith('شرح:'):
                current['شرح'] = line.replace('شرح:', '').strip()
        if current.get('سؤال'):
            current['الخيارات'] = options
            if 'الإجابة_الصحيحة' not in current and options:
                current['الإجابة_الصحيحة'] = options[0]
            questions.append(current)
        return questions[:num_questions]
    return None


def ai_generate_presentation(text, num_slides=8):
    """توليد محتوى عرض تقديمي بالذكاء الاصطناعي"""
    prompt = f"""أنشئ عرض تقديمي من {num_slides} شرائح من النص التالي بالعربية الفصحى.
لكل شريحة قدم عنوان ومحتوى (3-4 نقاط).
استخدم التنسيق:
عنوان: [عنوان الشريحة]
- [نقطة 1]
- [نقطة 2]
- [نقطة 3]
---

النص:
{text[:4000]}"""
    result = ai_generate(prompt)
    if result:
        slides = []
        current_title = ""
        current_points = []
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('عنوان:'):
                if current_title:
                    slides.append({
                        'عنوان': current_title,
                        'محتوى': current_points if current_points else [current_title],
                        'نوع': 'نقاط'
                    })
                current_title = line.replace('عنوان:', '').strip()
                current_points = []
            elif line.startswith('- ') or line.startswith('• '):
                current_points.append(line[2:].strip())
            elif line == '---':
                continue
        if current_title:
            slides.append({
                'عنوان': current_title,
                'محتوى': current_points if current_points else [current_title],
                'نوع': 'نقاط'
            })
        return slides[:num_slides]
    return None
