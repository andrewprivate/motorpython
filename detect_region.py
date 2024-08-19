import cv2
import os

def find_and_draw_rectangle(large_image_path, small_image_path):
    large_image = cv2.imread(large_image_path)
    small_image = cv2.imread(small_image_path)
    large_gray = cv2.cvtColor(large_image, cv2.COLOR_BGR2GRAY)
    small_gray = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(large_gray, small_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    top_left = max_loc
    h, w = small_gray.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)

    cv2.rectangle(large_image, top_left, bottom_right, (0, 255, 0), 2)

    center_x = (top_left[0] + bottom_right[0]) // 2
    center_y = (top_left[1] + bottom_right[1]) // 2

    base_name, ext = os.path.splitext(os.path.basename(large_image_path))

    coord_file_name = f"./{base_name}_detected_location_coordinates.txt"
    with open(coord_file_name, 'w') as f:
        f.write(f"Center Coordinates: ({center_x}, {center_y})\n")
    print(f"Center coordinates saved as {coord_file_name}")

    output_image_path = f"./{base_name}_detected_location{ext}"
    cv2.imwrite(output_image_path, large_image)
    print(f"Output image saved as {output_image_path}")

large_image_path = './Fused.jpg'
small_image_path = './Fused_cropped.jpg'

find_and_draw_rectangle(large_image_path, small_image_path)
