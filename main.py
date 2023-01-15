
#TODO: Before submitting, remove auto-classify/purge.sh
#TODO: Write the credits comment at the top of the file
#TODO: See how much space each run takes, set the delay so we gather as much data as possible whilst also keeping it under 3 GB

# This only classifies images into night/twilight/day, embeds the corresponding EXIF, and writes data to "data.csv".
# Our goal with this is to capture as much data as possible. We will process NDVI and O2 emissions back on Earth.

import cv2
from pathlib import Path
from PIL import Image
from pycoral.adapters import common
from pycoral.adapters import classify
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file
from picamera import PiCamera
import os
import shutil
from datetime import datetime, timedelta
from logzero import logger, logfile
import csv
from orbit import ISS
from file_checker import files_check
from gpiozero import CPUTemperature
from sense_emu import SenseHat # ! CHANGE sense_emu TO sense_hat BEFORE SUBMITTING
import re
from time import sleep

project_start_time = datetime.now()

base_folder = Path(__file__).parent.resolve()

model_file = f'{base_folder}/model_v1/model_edgetpu.tflite' # name of model
label_file = f'{base_folder}/model_v1/labels.txt' # Name of your label file
img_dir = f'{base_folder}/raw'
data_file = f'{base_folder}/data.csv'

# Functions for creating and appending data in a CSV file
def create_csv(data_file):
    with open(data_file, 'w') as f:
        try:
            writer = csv.writer(f)
            header = ("Image", "Type", "Longitude", "Latitude", "ISS Temperature", "CPU Temperature", "ISS Humidity")
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

# Function to convert raw coord. data into rationals

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

# Function to capture an image and embed it with the rationals converted above
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

interpreter = make_interpreter(f"{model_file}")
interpreter.allocate_tensors()

size = common.input_size(interpreter)

create_csv(data_file)
logfile(f'{base_folder}/events.log')
logger.debug("Hello from Romania !")
files_check(logger, base_folder)

try:
    logger.info(f"I run in {str(base_folder)}")
except:
    logger.error("Couldn\'t log the file location")

day_c = 0
night_c = 0
tw_c = 0

cam = PiCamera()
cam.resolution = (1296,972)

cpu = CPUTemperature()
sense = SenseHat()

has_been_killed = True

now_time = datetime.now()
while (now_time < project_start_time + timedelta(minutes=170)):
#for file in os.listdir(image_dir):
	#timestamp format: yyyy-mm-dd_hh-mm-ss
	timestamp = str(datetime.now())
	timestamp = timestamp[0:19]
	timestamp = re.sub(r'[:]', '-', re.sub(r'[ ]', '_', timestamp))

	#-----------------TAKE CAMERA PICTURE AND STORE IT IN image-----------------#
	image_file = f"{base_folder}/raw/{timestamp}.jpg"
	#take the picture
	point, latref, longref = capture(cam, image_file)

	image = Image.open(image_file).convert('RGB').resize(size, Image.ANTIALIAS)

	common.set_input(interpreter, image)
	interpreter.invoke()
	classes = classify.get_classes(interpreter, top_k=1)
	
	labels = read_label_file(label_file)
	for c in classes:

		cl = labels.get(c.id, c.id)
		logger.info(f'{image_file} {labels.get(c.id, c.id)} {c.score:.5f}')
		
		# move the image to the appropriate folder and count its type
		if cl == "night":
			night_c = night_c+1
			shutil.move(image_file, f"{base_folder}/auto-classify/night/")
		elif cl == "day":
			day_c = day_c+1
			shutil.move(image_file, f"{base_folder}/auto-classify/day/")
		elif cl == "twilight":
			tw_c = tw_c+1
			shutil.move(image_file, f"{base_folder}/auto-classify/twilight/")
	
	# Log to data.csv and logfile
	longitude = str(point.longitude).replace("deg", "°").replace("-", "") + longref
	latitude = str(point.latitude).replace("deg", "°").replace("-", "") + latref

	# log to logfile
	logger.info("Longitude: " + longitude)
	logger.info("Latitude: "  + latitude)

	iss_temp = sense.get_temperature()
	iss_humidity = sense.get_humidity()
	type = cl

	# write the csv row
	row = (timestamp, str(type), str(longitude), str(latitude), str(iss_temp), str(cpu.temperature), str(iss_humidity))
	add_csv_data(data_file, row)
	sleep(5)

	# add a line to the logfile so we can distinguish each run
	logger.debug("--------------------------------------------------")

	try:
		now_time = datetime.now()
	except:
		logger.error("Couldn't update the time")

logger.debug("Day: " + str(day_c))
logger.debug("Night: " + str(night_c))
logger.debug("Twilight: " + str(tw_c))
has_been_killed = False
logger.debug("Has been killed: " + str(has_been_killed))