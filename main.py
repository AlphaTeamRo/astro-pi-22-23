import cv2
import numpy as np
from functions.fastiecm import fastiecm

from functions.file_checker import files_check

from orbit import ISS
from picamera import PiCamera
from matplotlib import colors
from scipy.spatial import cKDTree as KDTree
from PIL import Image
from pathlib import Path
from datetime import datetime, timedelta
import re
import os
import csv
from logzero import logger, logfile

project_start_time = datetime.now()

base_folder = Path(__file__).parent.resolve()

# Functions for creating and appending data in a CSV file
def create_csv(data_file):
    with open(data_file, 'w') as f:
        try:
            writer = csv.writer(f)
            header = ("Image", "Healthy", "Declining", "Unhealthy", "Longitude", "Latitude", "O2 emissions", "ISS Temperature")
            writer.writerow(header)
        except:
            logger.error("Couldn't create a csv file")

def add_csv_data(data_file, data):
    with open(data_file, 'a') as f:
        try:
            writer = csv.writer(f)
            writer.writerow(data)
        except:
            logger.error("Couldn't add csv data")

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

    logger.info(counts)

    return counts


def convert(angle):
    """
    Convert a `skyfield` Angle to an EXIF-appropriate
    representation (rationals)
    e.g. 98° 34' 58.7 to "98/1,34/1,587/10"
    """
    try:
        sign, degrees, minutes, seconds = angle.signed_dms()
        exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
        return sign < 0, exif_angle
    except:
        logger.error("Couldn't convert skyfiled angle to EXIF")

def capture(camera, image):
    """Use `camera` to capture an `image` file with lat/long EXIF data."""
    point = ISS.coordinates()

    # Convert the latitude and longitude to EXIF-appropriate representations
    south, exif_latitude = convert(point.latitude)
    west, exif_longitude = convert(point.longitude)

    # Set the EXIF tags specifying the current location
    camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
    latref = camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    longref = camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"

    # Capture the image
    camera.capture(image)

    return point, latref, longref

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

img_dir = f'{base_folder}/raw'
data_file = f'{base_folder}/data.csv'
create_csv(data_file)
logfile(f'{base_folder}/events.log')
print("Hello from Romania !")
files_check(logger, base_folder)

try:
    logger.info(f"I run in {str(base_folder)}")
except:
    logger.error("Couldn\'t log the file location")

cam = PiCamera()
cam.resolution = (1296,972)

now_time = datetime.now()
while (now_time < project_start_time + timedelta(minutes=170)):

    #timestamp format: yyyy-mm-dd_hh-mm-ss
    timestamp = str(datetime.now())
    timestamp = timestamp[0:19]
    timestamp = re.sub(r'[:]', '-', re.sub(r'[ ]', '_', timestamp))

    #-----------------TAKE CAMERA PICTURE AND STORE IT IN image-----------------#
    image_file = f"{base_folder}/raw/{timestamp}.jpg"
    point, latref, longref = capture(cam, image_file)

    image = cv2.imread(image_file)
    #image = cv2.imread('park.png')

    #save the original image
    cv2.imwrite(f'{base_folder}/raw/{timestamp}.jpg', image)

    #PROCESS THE IMAGE TO GET THE NDVI DATA
    contrasted = contrast_stretch(image)
    ndvi = calc_ndvi(contrasted)
    ndvi_contrasted = contrast_stretch(ndvi)
    #add color mapping(could be removed later, if we work using shades of grey instead of colors)
    color_mapped_prep = ndvi_contrasted.astype(np.uint8)
    color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm)
    cv2.imwrite('color_mapped_image.png', color_mapped_image)

    counts = pixelcount('color_mapped_image.png')

    #calculate the heath index
    #green = healthy
    #yellow = declining
    #red = unhealthy
    allcounts = counts["red"] + counts["green"] + counts["yellow"]
    healthy = round((counts["green"] / allcounts) * 100)
    declining = round((counts["yellow"] / allcounts) * 100)
    unhealthy = round((counts["red"] / allcounts) * 100)

    logger.info("Healthy: " + str(healthy))
    logger.info("Declining: " + str(declining))
    logger.info("Unhealthy: " + str(unhealthy))

    longitude = str(point.longitude).replace("deg", "°").replace("-", "") + longref
    latitude = str(point.latitude).replace("deg", "°").replace("-", "") + latref

    logger.info("Longitude: "+ longitude)
    logger.info("Latitude: " + latitude)

    row = (timestamp, str(healthy), str(declining), str(unhealthy), str(longitude), str(latitude))
    add_csv_data(data_file, row)


    try:
        now_time = datetime.now()
    except:
        logger.error("Couldn't update the time")