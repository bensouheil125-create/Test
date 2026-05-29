#!/usr/bin/env python3
"""
📚 دراستي الذكية - مشغل التطبيق
═══════════════════════════════════
شغّل هذا الملف لتشغيل التطبيق مباشرة:
  python start.py

سيفتح المتصفح تلقائياً على: http://localhost:5000
"""
import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("  📚 دراستي الذكية - Study AI")
    print("=" * 50)
    print()
    
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    requirements = os.path.join(backend_dir, 'requirements.txt')
    
    # تثبيت المكتبات إذا لزم الأمر
    print("  [1/2] التحقق من المكتبات...")
    try:
        import flask
        import pdfplumber
        import gtts
        from PIL import Image
        print("  ✅ المكتبات مثبتة")
    except ImportError:
        print("  ⏳ تثبيت المكتبات المطلوبة...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', requirements, '-q'
        ])
        print("  ✅ تم تثبيت المكتبات")
    
    print("  [2/2] تشغيل الخادم...")
    print()
    print("  🌐 افتح في المتصفح: http://localhost:5000")
    print("  ⏹️  للإيقاف اضغط: Ctrl+C")
    print()
    print("=" * 50)
    
    # تشغيل التطبيق
    app_py = os.path.join(backend_dir, 'app.py')
    os.chdir(backend_dir)
    subprocess.call([sys.executable, app_py])

if __name__ == '__main__':
    main()
