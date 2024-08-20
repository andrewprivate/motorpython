import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import RectangleSelector
from PIL import Image
import os
import stagecontroller

z_focus_location = 47.15  # Z focus height
controller = stagecontroller.StageController(port='COM3', baudrate=9600, timeout=1)
controller.connect()
controller.home()

def on_select(eclick, erelease):
    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)

    # Ensure coordinates are within the image bounds
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.width, x2), min(image.height, y2)

    # Calculate center coordinates in pixel
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    # Crop the selected region
    cropped_image = image.crop((x1, y1, x2, y2))

    # Save the cropped image
    base_name, ext = os.path.splitext(os.path.basename(image_file))
    cropped_file_name = f"./{base_name}_cropped{ext}"
    cropped_image.save(cropped_file_name)
    print(f"Cropped image saved as {cropped_file_name}")

    # Save center coordinates to a text file
    coord_file_name = f"./{base_name}_cropped_center_coordinates.txt"
    with open(coord_file_name, 'w') as f:
        f.write(f"Center Coordinates: ({center_x}, {center_y})")
    print(f"Center coordinates saved as {coord_file_name}")

    # Conversion to stage coordinates
    initial_x = 246.5 - (360/675)  # Initial x location in stage coordinates
    initial_y = 243.0 - (640/675)  # Initial y location in stage coordinates
    conversion_factor = 675  # Conversion factor from pixels to mm (px/mm)

    stage_x = initial_x + center_x / conversion_factor
    stage_y = initial_y + center_y / conversion_factor
    stage_z = z_focus_location  # Z coordinate

    # Save stage coordinates to a text file, including z focus height
    stage_coord_file_name = f"./{base_name}_cropped_stage_coordinates.txt"
    with open(stage_coord_file_name, 'w') as f:
        f.write(f"Stage Coordinates: ({stage_x:.2f}, {stage_y:.2f}, {stage_z:.2f})")
    print(f"Stage coordinates saved as {stage_coord_file_name}")

    controller.move_to(stage_x, stage_y, stage_z)

def on_scroll(event):
    base_scale = 1.2
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()

    xdata = event.xdata
    ydata = event.ydata

    if event.button == 'up':
        scale_factor = 1 / base_scale
    elif event.button == 'down':
        scale_factor = base_scale
    else:
        scale_factor = 1
        print(event.button)

    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

    ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
    ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
    plt.draw()

image_file = './images/Fused.jpg'
image = Image.open(image_file)

fig, ax = plt.subplots(1)
ax.axis('off')
img = mpimg.imread(image_file)
ax.imshow(img)

rect_selector = RectangleSelector(ax, on_select, useblit=True, button=[1], minspanx=5, minspany=5, spancoords='pixels', interactive=True)

fig.canvas.mpl_connect('scroll_event', on_scroll)

plt.show()
