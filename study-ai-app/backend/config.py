"""إعدادات التطبيق - منصة دراستي الذكية"""
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'study-ai-secret-key-2024')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 ميجابايت كحد أقصى
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

    # إعدادات الذكاء الاصطناعي - يمكن تعيينها عبر متغيرات البيئة أو عبر واجهة التطبيق
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # النموذج المستخدم
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
