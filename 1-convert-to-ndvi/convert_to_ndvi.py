import cv2
import numpy as np
from fastiecm import fastiecm
import os
from pathlib import Path

base_folder = Path(__file__).parents[1]
print("Working in: " + str(base_folder))
img_folder = f'{base_folder}/auto-classify/day'

#temp function for displaying resulted images
def display(image, image_name):
    image = np.array(image, dtype=float)/float(255)
    shape = image.shape
    height = int(shape[0] / 2)
    width = int(shape[1] / 2)
    image = cv2.resize(image, (width, height))
    cv2.namedWindow(image_name)
    cv2.imshow(image_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#function for increasing the contrast of the image
def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

#function to calculate ndvi precentage
def calc_ndvi(image):
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom==0] = 0.01
    ndvi = (b.astype(float) - r) / bottom
    return ndvi

"""
for dir in os.listdir(img_folder):
    #check if the file is a folder
    if "." not in str(dir):
        print("Processing: " + str(dir))
"""

#create folder for ndvi images, first check if it already exists
if not os.path.exists(f"{base_folder}/images_ndvi/"):
    os.makedirs(f"{base_folder}/images_ndvi/")
#iterate through all images in the folder
for image_file in os.listdir(img_folder):
    image = cv2.imread(img_folder + "/" + image_file)
    ##print("Image file is: " + str(image_file))
    contrasted = contrast_stretch(image)
    #calculate ndvi
    ndvi = calc_ndvi(contrasted)
    #contrast ndvi again (might be temporary)
    ndvi_contrasted = contrast_stretch(ndvi)
    #add color mapping(could be removed later, if we work using shades of grey instead of colors)
    color_mapped_prep = ndvi_contrasted.astype(np.uint8)
    color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm)
    img_path = f"{base_folder}/images_ndvi/" + image_file
    cv2.imwrite(img_path, color_mapped_image)
    print("Converted: " + img_path)