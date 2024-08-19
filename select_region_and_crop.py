import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import RectangleSelector
from PIL import Image
import os

def on_select(eclick, erelease):
    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)

    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.width, x2), min(image.height, y2)

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    cropped_image = image.crop((x1, y1, x2, y2))

    base_name, ext = os.path.splitext(os.path.basename(image_file))

    cropped_file_name = f"./{base_name}_cropped{ext}"
    cropped_image.save(cropped_file_name)
    print(f"Cropped image saved as {cropped_file_name}")

    coord_file_name = f"./{base_name}_center_coordinates.txt"
    with open(coord_file_name, 'w') as f:
        f.write(f"Center Coordinates: ({center_x}, {center_y})")
    print(f"Center coordinates saved as {coord_file_name}")

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

image_file = './Fused.jpg'
image = Image.open(image_file)

fig, ax = plt.subplots(1)
ax.axis('off')
img = mpimg.imread(image_file)
ax.imshow(img)

rect_selector = RectangleSelector(ax, on_select, useblit=True, button=[1], minspanx=5, minspany=5, spancoords='pixels', interactive=True)

fig.canvas.mpl_connect('scroll_event', on_scroll)

plt.show()
