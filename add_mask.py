import os
from PIL import Image

img_folder = 'processed'
mask = Image.open("test_mask.png")

for image_file in os.listdir(img_folder):
    image = Image.open("processed/" + image_file)
    image.paste(mask, (0, 0), mask)
    image.save("masked/" + image_file)
    