"""خدمة معالجة ملفات PDF واستخراج النصوص"""
import os
import pdfplumber
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_path):
    """استخراج النص من ملف PDF"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
    except Exception:
        # محاولة ثانية باستخدام PyPDF2
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        except Exception as e2:
            raise Exception(f"فشل في استخراج النص من الملف: {str(e2)}")

    if not text.strip():
        raise Exception("الملف لا يحتوي على نص قابل للاستخراج")

    return text.strip()


def get_pdf_info(file_path):
    """الحصول على معلومات ملف PDF"""
    try:
        reader = PdfReader(file_path)
        info = {
            'عدد_الصفحات': len(reader.pages),
            'المؤلف': reader.metadata.author if reader.metadata and reader.metadata.author else 'غير محدد',
            'العنوان': reader.metadata.title if reader.metadata and reader.metadata.title else 'غير محدد',
        }
        return info
    except Exception:
        return {'عدد_الصفحات': 0, 'المؤلف': 'غير محدد', 'العنوان': 'غير محدد'}


def split_text_into_chunks(text, chunk_size=3000):
    """تقسيم النص إلى أجزاء للمعالجة"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1
        if current_size >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
