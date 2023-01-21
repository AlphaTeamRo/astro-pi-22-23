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
    use_colors = {k: colors.cnames[k] for k in ['red', 'green', 'yellow', 'purple', 'gray', 'black', 'blue']}

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

    import pylab

    pylab.clf()
    pylab.imshow(color_tuples[idx])
    pylab.savefig(f'{base_folder}/testtt.png')
    

    return counts

data_file = f'{base_folder}/data.csv'
create_csv(data_file)

# Main loop
for image in os.listdir(img_folder):
    print(f"{base_folder}/images_masked/day/" + image)
    counts = pixelcount(f"{base_folder}/images_masked/day/" + image)

    all_vegetation_px = counts["red"] + counts["green"] + counts["yellow"]

    # Calculate what % of the image is occupied by plants(no matter their health condition)
    all_image_px = counts["red"] + counts["green"] + counts["yellow"] + counts["gray"] + counts["black"] #blue is the mask, it will be ignored

    # Calculate how much of the image is occupied by plants
    plant_px_percentage = round((all_vegetation_px / all_image_px) * 100)
    print("Total plant precentage: " + str(plant_px_percentage) + "%")


    #calculate the heath index. (What % of plants are what)
    #green = healthy
    #yellow = declining
    #red = unhealthy
    healthy = round((counts["green"] / all_vegetation_px) * 100)
    declining = round((counts["yellow"] / all_vegetation_px) * 100)
    unhealthy = round((counts["red"] / all_vegetation_px) * 100)

    # TODO: We have the health index(healthy, declining, unhealthy) and the plant percentage(plant_px_percentage). Now we need to calculate the o2 emissions. One pixel is equal to ~200m^2
    # *: 36% din toata imaginea sunt plante, din alea 36%, 50% sunt sanatoase, 25% sunt in declin si 10% sunt bolnave. => din imaginea totala, 18% sunt sanatoase, 9% sunt in declin si 4% sunt bolnave. calculeaza o2 ca mai jos. *ms copilot
    #o2 emissions may not be calculated correctly, this is just what copilot suggested
    o2 = round((healthy * 0.5) + (declining * 0.25) + (unhealthy * 0.1))

    row = (image, str(healthy), str(declining), str(unhealthy), str(o2))
    add_csv_data(data_file, row)