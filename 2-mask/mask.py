import os
from PIL import Image
from pathlib import Path

base_folder = Path(__file__).parents[1]
print("Working in: " + str(base_folder))
img_folder = f'{base_folder}/images_ndvi'

mask = Image.open("test_mask.png")

"""
for dir in os.listdir(img_folder):
    #check if the file is a folder
    if "." not in str(dir):
        print("Processing: " + str(dir))
"""
#create folder for masked images, first check if it already exists
if not os.path.exists(f"{base_folder}/images_masked/"):
    os.makedirs(f"{base_folder}/images_masked/")
#iterate through all images in the folder
print(f"{base_folder}/images_ndvi/")
for image_file in os.listdir(f"{base_folder}/images_ndvi/"):
    print("Masked: " + image_file)
    image = Image.open(f"{base_folder}/images_ndvi/" + image_file)
    image.paste(mask, (0, 0), mask)
    image.save(f"{base_folder}/images_masked/" + image_file) 