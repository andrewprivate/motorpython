# Read images directory to geta list of pngs

# Convert coordinates to pixel values
# load one image to get dimensions
import json
import cv2 as cv;
import os

def get_focus_score(image):
    laplacian = cv.Laplacian(image, cv.CV_64F)
    variance = laplacian.var()
    
    return variance


def getImageFiles():
    images = []
    for filename in os.listdir("images"):
        if filename.endswith(".png"):
            images.append(filename)

    return images

def filterImages(images):
    new_images = []
    focus_scores = []
    for image in images:
        img = cv.imread("images/" + image)
        focus_score = get_focus_score(img)
        focus_scores.append(focus_score)
        print("Focus score for {}: {}".format(image, focus_score))

    mean_focus_score = sum(focus_scores) / len(focus_scores)
    std = (sum([(focus_score - mean_focus_score) ** 2 for focus_score in focus_scores]) / len(focus_scores)) ** 0.5
    print("Mean focus score: {}".format(mean_focus_score))
    print("Standard deviation: {}".format(std))

    for image, focus_score in zip(images, focus_scores):
        if focus_score > 10:
            new_images.append(image)
    
    print("Images after filtering: {}/{}".format(len(new_images), len(images)))
    
    return new_images

images = getImageFiles()

# Filter images based on focus score
# images = filterImages(images)

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

def getImageSize(filename):
    img = cv.imread("images/" + filename)
    return img.shape


size = getImageSize(images[0])

# Get unique x, y, z values
unique_x = list(set([(coordinate[0]) for coordinate in coordinates]))
unique_y = list(set([(coordinate[1]) for coordinate in coordinates]))
unique_z = list(set([(coordinate[2]) for coordinate in coordinates]))

# Get grid size
grid_x_size = len(unique_x)
grid_y_size = len(unique_y)
grid_z_size = len(unique_z)
overlap = 0.1049
overlap_x = 0.5
overlap_y = 0.12

print("Grid size: {}x{}x{}".format(grid_x_size, grid_y_size, grid_z_size))

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
    x = (coordinate[0] - min_x) / step_size_x * size[1]
    y = (coordinate[1] - min_y) / step_size_y * size[0]
    new_coordinates.append((x, y))





def createTileConfig(images, coordinates):
    with open("images/TileConfiguration.txt", "w") as file:
        file.write("# Define the number of dimensions we are working on\n")
        file.write("dim = 2\n")
        file.write("# Define the image coordinates (in pixels)\n")
        for image, coordinate in zip(images, coordinates):
            coordinateStr = "({}, {})".format(round(coordinate[0] * (1.0 - overlap_x)), round(coordinate[1] * (1.0 - overlap_y)))
            file.write("{}; ; {}\n".format(image, coordinateStr))

# Create a stitch configuration file
# {
#     "version": "1.0",
#     "mode": "2d",
#     "overlap": 0,
#     "tile_paths": [
#         "img1.png",
#         "img2.png",
#     ]
#     "tile_layout": [
#         [x, y, width, height],
#         [x, y, width, height],
#     ]
# }
def createStitchConfig(images, coordinates, size):
    config = {
        "version": "1.0",
        "mode": "2d",
        "overlap": 0.0,
        "fuse_mode": "overwrite",
        "tile_paths": images,
        "tile_layout": [],
        "alignment_file": "align_values.json"
    }

    for coordinate in coordinates:
        config["tile_layout"].append([round(coordinate[0] * (1.0-overlap)), round(coordinate[1] * (1.0-overlap)), size[0], size[1]])

    with open("images/stitch_config.json", "w") as file:
        json.dump(config, file)

def createStitchAlign(images, coordinates, size):
    indexes = list(range(len(images)))
    config = {
        "pairs": [],
        "subgraphs": [indexes],
        "offsets": [[]]
    }

    for coordinate in coordinates:
        config["offsets"][0].append([round(coordinate[0] * 0.68), round(coordinate[1] * 0.70)])

    with open("images/align_values.json", "w") as file:
        json.dump(config, file)

createTileConfig(images, new_coordinates)
print("Tile configuration file created")

# createStitchConfig(images, new_coordinates, size)
# print("Stitch configuration file created")

# createStitchAlign(images, new_coordinates, size)

# # Stitch, go to stitching/rust and run
# # cargo run [path to stitch config file]

# config_path = os.path.abspath("images/stitch_config.json")
# print("Stitching configuration file path: {}".format(config_path))

# # Run the stitching program after cd to stitching/rust, keep shell open
# import subprocess
# cwdpath = os.path.abspath("stitching/rust")
# print("Current working directory: {}".format(cwdpath))
# p = subprocess.Popen(["cargo", "run", config_path], cwd=cwdpath, shell=True)
# p.wait()