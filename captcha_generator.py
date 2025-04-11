import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def generate_captcha_text(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_captcha_image(text, filename):
    width, height = 150, 60
    image = Image.new('RGB', (width, height), (255, 255, 255))

    font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
    font = ImageFont.truetype(font_path, 36)
    draw = ImageDraw.Draw(image)

    # 使用 textbbox 计算文字尺寸
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    draw.text(((width - text_width) / 2, (height - text_height) / 2),
              text, font=font, fill=(0, 0, 0))

    # 干扰线
    for _ in range(5):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill='gray', width=1)

    # 模糊
    image = image.filter(ImageFilter.BLUR)

    output_path = os.path.join('static', 'captcha', filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
