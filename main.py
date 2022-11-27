import cv2
import numpy as np
from fastiecm import fastiecm

from matplotlib import colors
from scipy.spatial import cKDTree as KDTree
from PIL import Image
from pathlib import Path
from datetime import datetime, timedelta
import re

base_folder = Path(__file__).parent.resolve()

caming = cv2.imread('park.png')

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

#-----------------LOOP START-----------------#

#timestamp format: yyyy-mm-dd_hh-mm-ss
timestamp = str(datetime.now())
timestamp = timestamp[0:19]
timestamp = re.sub(r'[:]', '-', re.sub(r'[ ]', '_', timestamp))

#save the original image
cv2.imwrite(f'{base_folder}/raw/{timestamp}.png', caming)

#PROCESS THE IMAGE TO GET THE NDVI DATA
contrasted = contrast_stretch(caming)
ndvi = calc_ndvi(contrasted)
ndvi_contrasted = contrast_stretch(ndvi)
#add color mapping(could be removed later, if we work using shades of grey instead of colors)
color_mapped_prep = ndvi_contrasted.astype(np.uint8)
color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm)
cv2.imwrite('color_mapped_image.png', color_mapped_image)

#calculate the number of pixels in the image
def pixelcount(img):
    #save the image(temporary, for testing)
    #cv2.imwrite('ndvi.png', img)
    img = Image.open(img)
    #borrow a list of named colors from matplotlib
    use_colors = {k: colors.cnames[k] for k in ['red', 'green', 'yellow', 'purple']}
    
    #translate hexstring to RGB tuple
    named_colors = {k: tuple(map(int, (v[1:3], v[3:5], v[5:7]), 3*(16,)))
                    for k, v in use_colors.items()}
    ncol = len(named_colors)
    
    ncol -= 1
    no_match = named_colors.pop('purple')
    
    #make an array containing the RGB values 
    color_tuples = list(named_colors.values())
    color_tuples.append(no_match)
    color_tuples = np.array(color_tuples)
    color_names = list(named_colors)
    color_names.append('no match')

    #start the actual counting
    #build tree
    tree = KDTree(color_tuples[:-1])
    #tolerance for color match `inf` means use best match no matter how bad it may be
    tolerance = np.inf
    #find closest color in tree for each pixel in picture
    dist, idx = tree.query(img, distance_upper_bound=tolerance)
    #count and reattach names
    counts = dict(zip(color_names, np.bincount(idx.ravel(), None, ncol+1)))

    print(counts)

    #calculate the heath index
    #green = healthy
    #yellow = moderate
    #red = unhealthy
    allcounts = counts["red"] + counts["green"] + counts["yellow"]
    healthy = round((counts["green"] / allcounts) * 100)
    moderate = round((counts["yellow"] / allcounts) * 100)
    unhealthy = round((counts["red"] / allcounts) * 100)

    print("Healthy: " + str(healthy))
    print("Moderate: " + str(moderate))
    print("Unhealthy: " + str(unhealthy))
    

pixelcount('color_mapped_image.png')