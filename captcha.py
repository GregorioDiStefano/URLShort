from PIL import ImageDraw, Image, ImageFont
import random
import cStringIO
import hashlib
from settings import settings

size = { "width": 70, "height": 23 }
font = ImageFont.truetype("resources/1942.ttf", 26)

def random_point():
    return random.randint(0, size["width"]), random.randint(0, size["height"])

def make_captcha():
    text = ""
    output = cStringIO.StringIO()
    m = hashlib.md5()

    captcha = Image.new("RGB", (size["width"], size["height"]), "black")
    draw = ImageDraw.Draw(captcha)
    
    for i in range(settings["captcha_length"]):
        text += random.choice("abcdefghjkmnpqrstuvwxyz2345679")
    

    secret_hash = m.update(text + settings["secret_key"])
    secret_hash = m.hexdigest()

    for i in range(4):
        coords = random_point(), random_point()
        draw.line(coords, fill=(255, 200, 0, 255), width=1)

    draw.text((0, -5), text, font=font, fill=(255,200,0,255))
    captcha.save(output, format="GIF", qualitiy=10)

    return { "image_data": output.getvalue(), "hash": secret_hash }

def validate_captcha(text, expected_hash):
    m = hashlib.md5() 
    actual_hash = m.update(text + settings["secret_key"])
    actual_hash = m.hexdigest()
    return actual_hash == expected_hash
