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

def generateCard(value, color, card_clr) -> str:
    image = Image.new(mode="RGBA", size=(100, 150), color=card_clr)
    txt = Image.new(mode="RGBA", size=(100, 150), color=(255,255,255,0))
    transparent_helper = ImageDraw.Draw(txt)
    letter_position = (20, 12)
    color_position = (30, 40)
    font = ImageFont.truetype("cardfont.ttf", 100)
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
    link = f"poker_files/cards/{value}{color}.jpg"
    img.save(link)
    return link
    
def generateReverse(card_clr=(8, 11, 32, 100)) -> str:
    image = Image.new(mode="RGBA", size=(100,150), color=card_clr)

    logo = Image.open("discordlogo.png").convert("RGBA")
    
    ratio = image.width / logo.width
    logo = logo.resize((int(image.width * 0.5), int(logo.height * ratio * 0.5)))
    
    x = (image.width - logo.width) // 2
    y = (image.height - logo.height) // 2
    
    Image.alpha_composite(image, Image.new("RGBA", image.size))
    image.paste(logo, (x, y), logo)
    
    image.save("poker_files/reverse.png")
    
    return "poker_files/reverse.png"

def generateCommunityCards(cards) -> str:
    image = Image.new(mode="RGB", size=(560,170), color=(24, 129, 48))
    for e, card in enumerate(cards):
        card_img = Image.open(card.file)
        image.paste(card_img, ((10*(e+1)) + 100*e, 10))
    match len(cards):
        case 3:
            card_img = Image.open("poker_files/reverse.png")
            image.paste(card_img, (340, 10))
            image.paste(card_img, (450, 10))
        case 4:
            card_img = Image.open("poker_files/reverse.png")
            image.paste(card_img, (450, 10))
        case 5:
            pass
    
    fname = f"poker_files/community.png"
    image.save(fname)
    return fname