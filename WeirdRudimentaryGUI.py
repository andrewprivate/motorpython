import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
import cv2 as cv
from PIL import Image, ImageTk
import stagecontroller
import time

from test import takePicture, gridTakePicture, focusCameraByZ

#Random code stuff down here
controller = stagecontroller.StageController(port='COM3', baudrate=9600, timeout=1)
controller.connect()
moveOrStay = input("Do you want to stay here? Current position will be set to 0").strip()
if moveOrStay.lower() == 'stay':
    controller.current_position = [0, 0, 0]
else:
    controller.home()

def home_stage():
    controller.home()

def move():
    x, y, z = map(float, simpledialog.askstring("Input starting Coordinates", "Enter X Y Z:").strip().split())
    controller.move_to(x, y, z)

def home_x():
    controller.home(homeY=False, homeZ=False)

def home_y():
    controller.home(homeX=False, homeZ=False)

def home_z():
    controller.home(homeX=False, homeY=False)

def take_picture():
    takePicture(controller)

def grid_picture():
    sx, sy, sz = map(float, simpledialog.askstring("Input starting Coordinates", "Enter start X Y Z:").strip().split())
    ex, ey, ez = map(float, simpledialog.askstring("Input ending Coordinates", "Enter end X Y Z:").strip().split())
    stepSize = float(simpledialog.askstring("Input", "Enter step size:"))
    gridTakePicture(controller, sx, sy, sz, ex, ey, ez, stepSize, interval=2)

def focusCameraByZ():
    focusCameraByZ(controller)

def exit_app():
    root.destroy()



def update_video_feed():
    # Capture frame from camera
    ret, frame = camera.read()
    if ret:
        # Convert frame to ImageTk format
        img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the image in the label
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    # Call this function again after 10 ms
    video_label.after(10, update_video_feed)

# Initialize camera
camera = cv.VideoCapture(0)

# Create the main window
root = tk.Tk()
root.title("Stage Controller GUI")
PADY_SIZE = 50
# Create a frame for the buttons
frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.LEFT, padx=10, pady=10)

# Create buttons and assign functions
home_button = tk.Button(frame_buttons, text="Home", command=home_stage)
home_button.pack(pady=PADY_SIZE)

home_x_button = tk.Button(frame_buttons, text="Home X", command=home_x)
home_x_button.pack(pady=PADY_SIZE)

home_y_button = tk.Button(frame_buttons, text="Home Y", command=home_y)
home_y_button.pack(pady=PADY_SIZE)

home_z_button = tk.Button(frame_buttons, text="Home Z", command=home_z)
home_z_button.pack(pady=PADY_SIZE)

move_button = tk.Button(frame_buttons, text="Move To", command=move)
move_button.pack(pady=PADY_SIZE)

take_picture_button = tk.Button(frame_buttons, text="Take Picture", command=take_picture)
take_picture_button.pack(pady=PADY_SIZE)

grid_picture_button = tk.Button(frame_buttons, text="Focus", command=focusCameraByZ)
grid_picture_button.pack(pady=PADY_SIZE)

focus_button = tk.Button(frame_buttons, text="FocuEEs", command=focusCameraByZ)
grid_picture_button.pack(pady=PADY_SIZE)

exit_button = tk.Button(frame_buttons, text="Exit", command=exit_app)
exit_button.pack(pady=PADY_SIZE)

# Create a frame for the video feed
frame_video = tk.Frame(root)
frame_video.pack(side=tk.RIGHT, padx=10, pady=PADY_SIZE)

# Create a label in the video frame to display the video feed
video_label = tk.Label(frame_video)
video_label.pack()

# Start updating the video feed
update_video_feed()

# Run the GUI loop
root.mainloop()

# Release the camera when the app is closed
camera.release()
cv.destroyAllWindows()
