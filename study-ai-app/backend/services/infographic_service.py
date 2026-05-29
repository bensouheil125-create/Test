"""خدمة توليد الإنفوغرافيك"""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont


def create_infographic(title, key_points, output_path, width=800, height=1200):
    """إنشاء إنفوغرافيك من النقاط الرئيسية"""

    bg_color = (20, 20, 35)
    header_color = (70, 100, 200)
    accent_colors = [
        (76, 175, 80),
        (255, 152, 0),
        (156, 39, 176),
        (0, 188, 212),
        (244, 67, 54),
        (63, 81, 181),
        (255, 193, 7),
        (121, 85, 72),
    ]
    text_color = (255, 255, 255)

    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_paths = [
            '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
        ]
        font_title = None
        font_body = None
        font_number = None
        for fp in font_paths:
            if os.path.exists(fp):
                font_title = ImageFont.truetype(fp, 36)
                font_body = ImageFont.truetype(fp, 20)
                font_number = ImageFont.truetype(fp, 28)
                break
        if font_title is None:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()
            font_number = ImageFont.load_default()
    except Exception:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_number = ImageFont.load_default()

    # رسم الرأس
    draw.rectangle([(0, 0), (width, 100)], fill=header_color)
    title_text = title[:40]
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = bbox[2] - bbox[0]
    draw.text(((width - title_width) // 2, 30), title_text, font=font_title, fill=text_color)

    # رسم النقاط
    y_offset = 130
    point_height = (height - 160) // max(len(key_points), 1)

    for i, point in enumerate(key_points[:8]):
        color = accent_colors[i % len(accent_colors)]

        box_x = width - 80
        box_y = y_offset + 5
        draw.rounded_rectangle(
            [(box_x, box_y), (box_x + 50, box_y + 50)],
            radius=10,
            fill=color
        )

        num_text = str(i + 1)
        num_bbox = draw.textbbox((0, 0), num_text, font=font_number)
        num_w = num_bbox[2] - num_bbox[0]
        draw.text((box_x + (50 - num_w) // 2, box_y + 10), num_text, font=font_number, fill=text_color)

        draw.rectangle([(50, y_offset), (width - 100, y_offset + 2)], fill=color)

        wrapped = textwrap.wrap(point, width=45)
        for j, line in enumerate(wrapped[:3]):
            draw.text((50, y_offset + 15 + j * 25), line, font=font_body, fill=text_color)

        y_offset += point_height

    img.save(output_path, 'PNG')

    return {
        'نجاح': True,
        'مسار_الملف': output_path,
        'عدد_النقاط': len(key_points)
    }
