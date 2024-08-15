import sys
import time
import stagecontroller
import cv2 as cv


def get_focus_score(image):
    laplacian = cv.Laplacian(image, cv.CV_64F)
    variance = laplacian.var()
    
    return variance

def gridTakePicture(controller, startX, startY, startZ, endX, endY, endZ, numX, numY, numZ, interval = 2, delay = 2):
    diffX = endX - startX
    diffY = endY - startY
    diffZ = endZ - startZ

    stepSizeX = diffX / max(numX - 1, 1)
    stepSizeY = diffY / max(numY - 1, 1)
    stepSizeZ = diffZ / max(numZ - 1, 1)

    print("Taking pictures in a grid from ({}, {}, {}) to ({}, {}, {})".format(startX, startY, startZ, endX, endY, endZ))
    # Count number of pictures to be taken
    numPictures = numX * numY * numZ
    print("Number of pictures to be taken: {}".format(numPictures))

    camera = cv.VideoCapture(0)

    for i in range(numX):
        x = startX + i * stepSizeX
        for j in range(numY):
            y = startY + j * stepSizeY
            for k in range(numZ):
                z = startZ + k * stepSizeZ

                print("Moving to coordinates ({}, {}, {})".format(x, y, z))
                controller.move_to(x, y, z, interval)
                # Take picture here
                time.sleep(delay)
                takePicture(controller, camera)

                count = i * numY * numZ + j * numZ + k + 1
                print("Picture {} of {} taken".format(count, numPictures))

    camera.release()

        
def focusCameraByZ(controller):
    camera = cv.VideoCapture(0)

    scale = controller.get_scale()
    current_pos = controller.get_position()

    imagesPerScale = 5
    numScales = 8

    minZ = 0
    maxZ = 60

    # Maximize focus score, search along grid, then refine
    bestFocus = 0
    bestZ = 0
    zAccumulator = (maxZ - minZ) / 2

    for i in range(numScales):
        division = (maxZ - minZ) / ((imagesPerScale) ** (i * 0.5 + 1))

        if division < 1/scale[2]:
            division = 1/scale[2]

        bestCurrentFocus = 0
        bestCurrentZ = 0
        for j in range(imagesPerScale):
            z = minZ + (j - imagesPerScale / 2) * division + zAccumulator
            if z < minZ or z > maxZ:
                continue

            print("Moving to z = {}".format(z))
            controller.move_to(current_pos[0], current_pos[1], z)
            time.sleep(3)
            img = takePicture(controller, camera, save=False)
            focus = get_focus_score(img)
            
            print("Focus score: {}".format(focus))

            new_filename = "images/focus_{}_{}.png".format(round(z,5), focus)
            cv.imwrite(new_filename, img)

            if focus > bestCurrentFocus:
                bestCurrentFocus = focus
                bestCurrentZ = z
        
        zAccumulator = bestCurrentZ
        if bestCurrentFocus > bestFocus:
            bestZ = bestCurrentZ
            bestFocus = bestCurrentFocus

        if division <= 1/scale[2]:
            break

    print("Best focus: {} at z = {}".format(bestFocus, bestZ))
    controller.move_to(current_pos[0], current_pos[1], bestZ)

    camera.release()


def takePicture(controller, cameraIn = None, filename = None, save = True):
    x = controller.get_position()[0]
    y = controller.get_position()[1]
    z = controller.get_position()[2]

    # Round to 2 decimal places
    x = round(x, 2)
    y = round(y, 2)
    z = round(z, 2)

    print("Taking picture at coordinates ({}, {}, {})".format(x, y, z))
    # Take picture here

    try:
        if cameraIn:
            camera = cameraIn
        else:
            camera = cv.VideoCapture(0)
        img = camera.read()[1]
        # Save image
        if not filename:
            filename = "images/image_{}_{}_{}.png".format(x, y, z)
        
        # print dimensions of image
        print("Image dimensions: {}".format(img.shape))

        if save:
            cv.imwrite(filename, img)
        
        if not cameraIn:
            camera.release()

        return img
    except:
        print("Error taking picture")
        print(sys.exc_info()[0])
        return




def main():
    # Initialize and connect to the stage controller
    controller = stagecontroller.StageController(port='COM3', baudrate=9600, timeout=1)
    controller.connect()

    # Home the stage initially
    controller.home()

    while True:
        try:
            # Request user input
            command = input("Enter command (or coordinates as X Y Z): ").strip()

            if command.lower() == 'picture':
                takePicture(controller)
            elif command.lower() == 'grid':
                # query user
                #print("Enter start x, y, z/n")
                startPos = input("Enter start x y z: ").strip().split()
                if len(startPos) != 3:
                    print("Invalid input. Please enter three numeric values separated by spaces.")
                    continue

                #print("Enter end x, y, z/n")
                endPos = input("Enter end x y z: ").strip().split()
                if len(endPos) != 3:
                    print("Invalid input. Please enter three numeric values separated by spaces.")
                    continue

                stepNum = input("Enter number of steps in x, y, z: ").strip().split()
                if len(stepNum) != 3:
                    print("Invalid input. Please enter three numeric values separated by spaces.")
                    continue

                numX, numY, numZ = map(int, stepNum)

                interval = 2
                delay = float(input("Enter delay: "))

                startX, startY, startZ = map(float, startPos)
                endX, endY, endZ = map(float, endPos)

                gridTakePicture(controller, startX, startY, startZ, endX, endY, endZ, numX, numY, numZ, interval, delay)

            elif command.lower() == 'home':
                # Home the stage
                print("Homing the stage...")
                controller.home()
            elif command.lower() == 'focus':
                focusCameraByZ(controller)
            elif command.lower() == 'homex':
                # Home the stage
                print("Homing the stage along x")
                controller.home(homeY=False, homeZ = False)
            elif command.lower() == 'homey':
                # Home the stage
                print("Homing the stage along y")
                controller.home(homeX = False, homeZ = False)
            elif command.lower() == 'homez':
                # Home the stage
                print("Homing the stage along z")
                controller.home(homeX = False, homeY = False)
            else:
                # Parse coordinates from the command input
                coords = command.split()
                if len(coords) == 3:
                    try:
                        x, y, z = map(float, coords)
                        # Move the stage to the specified coordinates
                        print(f"Moving to coordinates ({x}, {y}, {z})...")
                        controller.move_to(x, y, z, interval=2)
                    except ValueError:
                        print("Invalid coordinates. Please enter three numeric values.")
                else:
                    print("Invalid input. Please enter 'home' or three numeric values separated by spaces.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
