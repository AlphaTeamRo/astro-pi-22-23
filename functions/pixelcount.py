from matplotlib import colors
from scipy.spatial import cKDTree as KDTree
from PIL import Image
import numpy as np

#calculate the number of pixels in the image
def pixelcount(img, logger):
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

    #calculate the heath index
    #green = healthy
    #yellow = moderate
    #red = unhealthy
    allcounts = counts["red"] + counts["green"] + counts["yellow"]
    healthy = round((counts["green"] / allcounts) * 100)
    moderate = round((counts["yellow"] / allcounts) * 100)
    unhealthy = round((counts["red"] / allcounts) * 100)

    logger.info("Healthy: " + str(healthy))
    logger.info("Moderate: " + str(moderate))
    logger.info("Unhealthy: " + str(unhealthy))