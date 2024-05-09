from PIL import Image, ImageDraw, ImageFont
from tkinter import Tk

root = Tk()
img = Image.open("images/whiteCircle.png")
imgSize = 250
img = img.resize((imgSize, imgSize))
img.save("images/whiteCircle.png")#"""
#img = img.convert("RGB") -> removes transparency

d = img.getdata()

new_image = []
tkinterColor = 'navy'
tkinterColor = 'red3'

colorRGB = tuple((c//256 for c in root.winfo_rgb(tkinterColor)))
for item in d:

    # change all white (also shades of whites)
    # pixels to yellow
    if item[0] in list(range(200,256)):
        new_image.append(colorRGB)
    else:
        new_image.append(item)

# update image data
img.putdata(new_image)

# save new image
img.save(f"images/{tkinterColor}Circle.png")

draw = ImageDraw.Draw(img)
myFont = ImageFont.truetype('arial.ttf', imgSize//2)

txt = "M"

draw.text((imgSize//3.424, imgSize//4.386), txt, font=myFont, fill=(0,0,0))
img.save(f"images/{tkinterColor}Circle{txt}.png")#"""