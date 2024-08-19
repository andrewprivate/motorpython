# Read images directory to geta list of pngs

import os

def getImageFiles():
    images = []
    for filename in os.listdir("images"):
        if filename.endswith(".png"):
            images.append(filename)

    return images


images = getImageFiles()

# Image file name format image_x_y_z.png
# Find x, y, z values from image file name

def getCoordinates(filename):
    # Remove .png from filename
    filename = filename[:-4]
    # Split filename by _
    parts = filename.split("_")
    x = float(parts[1])
    y = float(parts[2])
    z = float(parts[3])

    return (x, y, z)

# Get coordinates for each image
coordinates = [getCoordinates(image) for image in images]

# Create a tile configuration file
# Format
# # Define the number of dimensions we are working on
# dim = 2
# # Define the image coordinates (in pixels)
# img_73.tif; ; (0.0, 0.0, 0.0)
# img_74.tif; ; (409.0, 0.0, 0.0)
# img_75.tif; ; (0.0, 409.0, 0.0)
# img_76.tif; ; (409.0, 409.0, 0.0)
# img_77.tif; ; (0.0, 818.0, 0.0)
# img_78.tif; ; (409.0, 818.0, 0.0)

print(coordinates)

# Convert coordinates to pixel values
# load one image to get dimensions
import cv2 as cv;

def getImageSize(filename):
    img = cv.imread("images/" + filename)
    return img.shape


size = getImageSize(images[0])

grid_x_size = 15
grid_y_size = 30
overlap = 0.5

def getMinMaxCoordinates(coordinates):
    min_x = min([coordinate[0] for coordinate in coordinates])
    max_x = max([coordinate[0] for coordinate in coordinates])

    min_y = min([coordinate[1] for coordinate in coordinates])
    max_y = max([coordinate[1] for coordinate in coordinates])

    return min_x, max_x, min_y, max_y

min_x, max_x, min_y, max_y = getMinMaxCoordinates(coordinates)

diff_x = max_x - min_x
diff_y = max_y - min_y

step_size_x = diff_x / (grid_x_size - 1)
step_size_y = diff_y / (grid_y_size - 1)

print("Step size x: {}".format(step_size_x))

new_coordinates = []
for coordinate in coordinates:
    x = (coordinate[0] - min_x) / step_size_x * size[1] * overlap
    y = (coordinate[1] - min_y) / step_size_y * size[0] * overlap
    new_coordinates.append((x, y))





def createTileConfig(images, coordinates):
    with open("images/TileConfiguration.txt", "w") as file:
        file.write("# Define the number of dimensions we are working on\n")
        file.write("dim = 2\n")
        file.write("# Define the image coordinates (in pixels)\n")
        for image, coordinate in zip(images, coordinates):
            coordinateStr = "({}, {})".format(round(coordinate[0]), round(coordinate[1]))
            file.write("{}; ; {}\n".format(image, coordinateStr))

createTileConfig(images, new_coordinates)
print("Tile configuration file created")