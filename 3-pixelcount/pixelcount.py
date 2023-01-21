from matplotlib import colors
from scipy.spatial import cKDTree as KDTree
from PIL import Image
import numpy as np
import csv
from pathlib import Path
import os

base_folder = Path(__file__).parents[1]
print("Working in: " + str(base_folder))
img_folder = f'{base_folder}/images_masked/day'


# Functions for creating and appending data in a CSV file
def create_csv(data_file):
    with open(data_file, 'w') as f:
        try:
            writer = csv.writer(f)
            header = ("Image", "Healthy", "Declining", "Unhealthy", "O2 emissions")
            writer.writerow(header)
        except:
            print("Couldn't create a csv file")

def add_csv_data(data_file, data):
    with open(data_file, 'a') as f:
        try:
            writer = csv.writer(f)
            writer.writerow(data)
        except:
            print("Couldn't add csv data")

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
    # convert RGBA to RGB
    img = img.convert("RGB")
    #find closest color in tree for each pixel in picture
    dist, idx = tree.query(img, distance_upper_bound=tolerance)
    #count and reattach names
    counts = dict(zip(color_names, np.bincount(idx.ravel(), None, ncol+1)))

    print(counts)
    

    return counts

data_file = f'{base_folder}/data.csv'
create_csv(data_file)

# Main loop
for image in os.listdir(img_folder):
    print(f"{base_folder}/images_masked/day/" + image)
    counts = pixelcount(f"{base_folder}/images_masked/day/" + image)

    #calculate the heath index
    #green = healthy
    #yellow = declining
    #red = unhealthy
    allcounts = counts["red"] + counts["green"] + counts["yellow"]
    healthy = round((counts["green"] / allcounts) * 100)
    declining = round((counts["yellow"] / allcounts) * 100)
    unhealthy = round((counts["red"] / allcounts) * 100)

    #o2 emissions may not be calculated correctly, this is just what copilot suggested
    o2 = round((healthy * 0.5) + (declining * 0.25) + (unhealthy * 0.1))

    row = (image, str(healthy), str(declining), str(unhealthy), str(o2))
    add_csv_data(data_file, row)