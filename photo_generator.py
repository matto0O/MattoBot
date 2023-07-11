from PIL import Image, ImageFont, ImageDraw

def generate(width: int, height: int, message: str, name:str):
    img = Image.new(mode="RGB", size=(width, height), color=(255,255,255))
    fontsize = 1
    font = ImageFont.truetype("cour.ttf", fontsize-1)
    split = message.split('\n')[1]
    while font.getsize(split)[0] < img.size[0] and font.getsize(split)[1] < img.size[1]:
        fontsize += 1
        font = ImageFont.truetype("cour.ttf", fontsize)
    font = ImageFont.truetype("cour.ttf", fontsize-1)
    draw_helper = ImageDraw.Draw(img)
    draw_helper.text((0,0), message, (0,0,0), font=font)
    img = img.save(name)

def generateCard(value, color, card_clr):
    image = Image.new(mode="RGBA", size=(200, 300), color=card_clr)
    txt = Image.new(mode="RGBA", size=(200, 300), color=(255,255,255,0))
    transparent_helper = ImageDraw.Draw(txt)
    letter_position = (40, 25)
    color_position = (60, 80)
    font = ImageFont.truetype("cardfont.ttf", 200)
    draw_helper = ImageDraw.Draw(image)
    match color:
        case 's':
            transparent_helper.text(color_position, '}', (255, 255, 255, 30), font=font)
        case 'h':
            transparent_helper.text(color_position, '{', (255, 255, 255, 30), font=font)
        case 'd':
            transparent_helper.text(color_position, '[', (255, 255, 255, 30), font=font)
        case 'c':
            transparent_helper.text(color_position, ']', (255, 255, 255, 30), font=font)
    draw_helper.text(letter_position, value, (255, 255, 255, 100), font=font)
    image = Image.alpha_composite(image, txt)
    img = image.convert('RGB')
    link = f"cards/{value}{color}.jpg"
    img.save(link)
    return link
    
    
