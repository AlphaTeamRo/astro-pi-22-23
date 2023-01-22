from matplotlib import colors
from scipy.spatial import cKDTree as KDTree
from PIL import Image
import numpy as np
import csv
from pathlib import Path
import os

base_folder = Path(__file__).parents[1]
print("Working in: " + str(base_folder))
# * Only analyze the day images
img_folder = f'{base_folder}/images_masked/'


# Functions for creating and appending data in a CSV file
def create_csv(data_file):
    with open(data_file, 'w', newline='') as f:
        try:
            writer = csv.writer(f)
            header = ("Image", "Healthy%", "Declining%", "Unhealthy%", "No plants%", "O2 emissions (grams)", "CO2 removal (grams)")
            writer.writerow(header)
        except:
            print("Couldn't create a csv file")

def add_csv_data(data_file, data):
    with open(data_file, 'a', newline='') as f:
        try:
            writer = csv.writer(f)
            writer.writerow(data)
        except:
            print("Couldn't add csv data")

#calculate the number of pixels in the image
def pixelcount(img):
    #save the image(temporary, for testing)
    #cv2.imwrite('ndvi.png', img)
    img_name = img.split("/")[-1]
    img = Image.open(img)
    #borrow a list of named colors from matplotlib
    use_colors = {k: colors.cnames[k] for k in ['red', 'green', 'lime', 'limegreen', 'yellow', 'orange', 'purple', 'gray', 'black', 'blue']}

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
    pylab.savefig(f'{base_folder}/images_plain_colors/{img_name.split(".")[0]}.jpg')
    

    return counts

data_file = f'{base_folder}/data.csv'
create_csv(data_file)

#create folder for plain images, first check if it already exists
if not os.path.exists(f"{base_folder}/images_plain_colors/"):
    os.makedirs(f"{base_folder}/images_plain_colors/")

# Main loop
for image in os.listdir(img_folder):
    print(img_folder + image)
    counts = pixelcount(img_folder + image)

    green = counts["green"] + counts["lime"] + counts["limegreen"]
    yellow = counts["yellow"] + counts["orange"]
    red = counts["red"]
    none = counts["gray"] + counts["black"]

    # Calculate how much of the image is occupied by plants
    total_plants = red + green + yellow
    # Calculate what % of the image is occupied by plants(no matter their health condition)
    total = red + green + yellow + none #blue is the mask, it will be ignored

    
    all_image_px = counts["red"] + green + yellow + counts["gray"] + counts["black"] #blue is the mask, it will be ignored
    
    #calculate the heath index. (What % of plants are what)
    #green = healthy
    #yellow = declining
    #red = unhealthy
    healthy_perc = round(green / total * 10000) / 100
    declining_perc = round(yellow / total * 10000) / 100
    unhealthy_perc = round(red / total * 10000) / 100
    none_perc = round(none / total * 10000) / 100
    #print
    print("Healthy: " + str(healthy_perc) + "%")
    print("Declining: " + str(declining_perc) + "%")
    print("Unhealthy: " + str(unhealthy_perc) + "%")
    print("None: " + str(none_perc) + "%")
    

    # TODO: We have the health index(healthy%, declining%, unhealthy% and none%). Now we need to calculate the o2 emissions. One pixel is equal to ~200m^2
    # *: 36% din toata imaginea sunt plante, din alea 36%, 50% sunt sanatoase, 25% sunt in declin si 10% sunt bolnave. => din imaginea totala, 18% sunt sanatoase, 9% sunt in declin si 4% sunt bolnlave si 63% e spatiu fara plante. calculeaza o2 ca mai jos. *ms copilot
    #o2 emissions may not be calculated correctly, this is just what copilot suggested
    ##o2 = round((healthy * 0.5) + (declining * 0.25) + (unhealthy * 0.1))

    # Given that one pixel is equal to ~200m^2, and 200m^2 of HEALTHY grass produces on average 0.031 g O2/day and removes 42 g CO2/day
    # We can approximate the o2 emmisions/co2 removal of declining plants at 0.015 g O2/day and 21 g CO2/day (50%) and unhealthy plants at 0.005 g O2/day and 7 g CO2/day (10%)
    # We can approximate the o2 emmisions/co2 removal of no plants at 0.000 g O2/day and 0 g CO2/day (0%)
    # green = healthy, yellow = declining, red = unhealthy, none = no plants
    #calculate the o2 emissions
    o2 = round((green * 0.031) + (yellow * 0.015) + (red * 0.005) + (none * 0.000))
    #calculate the co2 removal
    co2 = round((green * 42) + (yellow * 21) + (red * 7) + (none * 0))

    row = (image, str(healthy_perc), str(declining_perc), str(unhealthy_perc), str(none_perc), str(o2), str(co2))
    add_csv_data(data_file, row)