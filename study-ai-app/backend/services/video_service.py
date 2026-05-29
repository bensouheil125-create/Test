"""خدمة توليد الفيديوهات التعليمية"""
import os
import textwrap
import subprocess
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS


def create_text_frame(text, output_path, width=1280, height=720,
                      bg_color=(20, 20, 40), text_color=(255, 255, 255)):
    """إنشاء إطار نصي (صورة) للفيديو"""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    font_size = 32
    try:
        font_paths = [
            '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
        ]
        font = None
        for fp in font_paths:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, font_size)
                break
        if font is None:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=40)
    total_height = len(lines) * (font_size + 15)
    y_start = (height - total_height) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = y_start + i * (font_size + 15)
        draw.text((x, y), line, font=font, fill=text_color)

    img.save(output_path)
    return output_path


def generate_video_from_text(text, output_path, title="ملخص الكتاب"):
    """توليد فيديو تعليمي من النص"""
    temp_dir = os.path.dirname(output_path)
    frames_dir = os.path.join(temp_dir, 'frames')
    os.makedirs(frames_dir, exist_ok=True)

    # تقسيم النص إلى مقاطع
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    segments = []
    current_segment = []

    for sentence in sentences:
        current_segment.append(sentence)
        if len(' '.join(current_segment)) > 150:
            segments.append(' '.join(current_segment))
            current_segment = []

    if current_segment:
        segments.append(' '.join(current_segment))

    segments = segments[:10]
    if not segments:
        segments = [text[:500]]

    # إنشاء إطار العنوان
    title_frame = os.path.join(frames_dir, 'frame_000.png')
    create_text_frame(title, title_frame, bg_color=(15, 15, 50))

    frame_paths = [title_frame]
    for i, segment in enumerate(segments):
        frame_path = os.path.join(frames_dir, f'frame_{i + 1:03d}.png')
        create_text_frame(segment, frame_path)
        frame_paths.append(frame_path)

    # إنشاء الصوت
    full_text = title + ". " + ". ".join(segments)
    audio_path = os.path.join(temp_dir, 'audio.mp3')
    tts = gTTS(text=full_text[:5000], lang='ar', slow=False)
    tts.save(audio_path)

    # حساب مدة كل إطار
    total_duration = len(full_text[:5000]) / 10
    frame_duration = total_duration / len(frame_paths)

    # إنشاء ملف concat
    concat_file = os.path.join(temp_dir, 'concat.txt')
    with open(concat_file, 'w') as f:
        for frame_path in frame_paths:
            f.write(f"file '{frame_path}'\n")
            f.write(f"duration {frame_duration}\n")
        f.write(f"file '{frame_paths[-1]}'\n")

    try:
        video_no_audio = os.path.join(temp_dir, 'video_no_audio.mp4')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file,
            '-vf', 'scale=1280:720',
            '-pix_fmt', 'yuv420p',
            '-r', '1',
            video_no_audio
        ], capture_output=True, timeout=120)

        subprocess.run([
            'ffmpeg', '-y',
            '-i', video_no_audio,
            '-i', audio_path,
            '-c:v', 'copy', '-c:a', 'aac',
            '-shortest',
            output_path
        ], capture_output=True, timeout=120)

        if os.path.exists(video_no_audio):
            os.remove(video_no_audio)

        return {
            'نجاح': True,
            'مسار_الملف': output_path,
            'عدد_المقاطع': len(segments),
            'المدة_التقريبية': f"{int(total_duration)} ثانية"
        }
    except FileNotFoundError:
        return {
            'نجاح': True,
            'مسار_الصوت': audio_path,
            'مسارات_الإطارات': frame_paths,
            'ملاحظة': 'تم إنشاء الصوت والصور. يلزم تثبيت ffmpeg لإنشاء الفيديو الكامل',
            'عدد_المقاطع': len(segments)
        }
    except Exception as e:
        return {
            'نجاح': False,
            'خطأ': str(e)
        }
