import cv2
import numpy as np
from functions.fastiecm import fastiecm
from functions.pixelcount import pixelcount
from functions.file_checker import files_check

from orbit import ISS
from picamera import PiCamera

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
            header = ("Date/time", "Country", "City", "Weather")
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
    camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"

    # Capture the image
    camera.capture(image)

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
    capture(cam, image_file)

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

    pixelcount('color_mapped_image.png', logger)


    try:
        now_time = datetime.now()
    except:
        logger.error("Couldn't update the time")