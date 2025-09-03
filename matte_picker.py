import os
from tkinter import *
import PIL
from PIL import Image, ImageCms, ImageTk
from functools import partial
import cv2
import numpy as np


# use k means cluster on a reduced resolution image to find common colors
def get_common_colors(img, num_colors=10):
    # Reshape the image to a 2D array of pixels
    small_img = img.resize((img.width // 2, img.height // 2), PIL.Image.LANCZOS)
    pixel_values = np.array(small_img.getdata()).reshape(small_img.size[1], small_img.size[0], 3)
    pixel_values = np.float32(pixel_values.reshape((-1, 3)))

    # Define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    k = num_colors
    _, _, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    # Convert back to 8 bit values
    centers = np.uint8(centers)
    return centers

def rgb_to_lab(rgb_tuple):
    # Create a 1x1 image with the RGB color
    rgb_img = Image.new("RGB", (1, 1), rgb_tuple)
    srgb_profile = ImageCms.createProfile("sRGB")
    lab_profile = ImageCms.createProfile("LAB")
    transform = ImageCms.buildTransform(srgb_profile, lab_profile, "RGB", "LAB")
    lab_img = ImageCms.applyTransform(rgb_img, transform)
    # Get LAB value as a tuple
    return lab_img.getpixel((0, 0))

def lab_to_rgb(lab_tuple):
    # Create a 1x1 image with the LAB color
    lab_img = Image.new("LAB", (1, 1), lab_tuple)
    srgb_profile = ImageCms.createProfile("sRGB")
    lab_profile = ImageCms.createProfile("LAB")
    transform = ImageCms.buildTransform(lab_profile, srgb_profile, "LAB", "RGB")
    rgb_img = ImageCms.applyTransform(lab_img, transform)
    # Get RGB value as a tuple
    return rgb_img.getpixel((0, 0))

def rgb_to_hex_string(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

class MattePicker:

    def load_image(self, image_filename):
        img = Image.open(image_filename)

        # compute optimal scale and resize
        if img.size[0]/img.size[1] > (self.target_size[0] - self.minimum_border)/(self.target_size[1] - self.minimum_border):
            scale = (self.target_size[0] - self.minimum_border) / img.size[0]
        else:
            scale = (self.target_size[1] - self.minimum_border) / img.size[1]
        self.img_resized = img.resize((int(img.size[0]*scale), int(img.size[1]*scale)), PIL.Image.BILINEAR if scale > 1.0 else  PIL.Image.LANCZOS)

        # compute border colors and apply to buttons
        common_colors = get_common_colors(self.img_resized, self.number_of_colors)

        button = iter(self.buttons)
        for color in common_colors:
            target_color_lab = rgb_to_lab(tuple(color))
            if target_color_lab[0] < 128:
                next(button).config(bg=rgb_to_hex_string(
                    lab_to_rgb((int(target_color_lab[0] * 0.3 + 20), target_color_lab[1], target_color_lab[2]))))
                next(button).config(bg=rgb_to_hex_string(
                    lab_to_rgb((int(target_color_lab[0] * 0.3 + 180), target_color_lab[1], target_color_lab[2]))))
            else:
                next(button).config(bg=rgb_to_hex_string(
                    lab_to_rgb((int(target_color_lab[0] * 0.3), target_color_lab[1], target_color_lab[2]))))
                next(button).config(bg=rgb_to_hex_string(
                    lab_to_rgb((int(target_color_lab[0] * 0.3 + 120), target_color_lab[1], target_color_lab[2]))))

        self.apply_border(self.buttons[0].cget("bg"))

    def apply_border(self, color):
        self.img_bordered = Image.new('RGB', self.target_size, color)
        self.img_bordered.paste(self.img_resized, ((self.target_size[0] - self.img_resized.size[0]) // 2, (self.target_size[1] - self.img_resized.size[1]) // 2))
        self.img_tk = ImageTk.PhotoImage(self.img_bordered.resize((self.img_bordered.width // 2, self.img_bordered.height // 2), PIL.Image.LANCZOS))
        self.canvas.itemconfig(self.image_container,image=self.img_tk)

    def button_callback(self, button_index):
        selected_color = self.buttons[button_index].cget("bg")
        self.apply_border(selected_color)

    def next_image(self):
        # Save processed image
        output_path = os.path.join(self.output_dir, self.image_files[self.file_counter])
        self.img_bordered.save(output_path,'jpeg',quality=95, optimize=True)

        self.file_counter += 1
        if self.file_counter == len(self.image_files):
            self.ws.destroy()
        else:
            self.load_image(self.image_files[self.file_counter])

    def __init__(self):
        # Configuration
        self.input_dir = '.'                # Directory containing images
        self.output_dir = './output_images' # Directory to save processed images
        self.target_size = (3840, 2160)     # desired final size with matting
        self.minimum_border = 120           # Minimum border width in pixels
        self.number_of_colors = 8           # Number of colors to extract

        os.makedirs(self.output_dir, exist_ok=True)

        # Supported image extensions
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

        # gather up image files
        self.image_files = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(image_extensions):
                img_path = os.path.join(self.input_dir, filename)
                self.image_files.append(img_path)

        # create a user interface
        self.ws = Tk()
        self.ws.title('Matte Picker')
        self.ws.geometry('2000x1080')

        self.canvas = Canvas(
            self.ws,
            width=self.target_size[0]*0.5,
            height=self.target_size[1]*0.5
        )
        self.canvas.place(x = 0, y = 0, anchor=NW)

        self.img_bordered = Image.new('RGB', self.target_size, (255, 255, 255))
        img_tk = ImageTk.PhotoImage(self.img_bordered.resize((self.img_bordered.width // 2, self.img_bordered.height // 2), PIL.Image.LANCZOS))
        self.image_container = self.canvas.create_image(0, 0, anchor=NW, image=img_tk)

        # add the color patch buttons
        self.buttons = []
        for i in range(0,self.number_of_colors*2):
            button = Button(self.ws, command= partial(self.button_callback, i))
            button.place(x = self.target_size[0]*0.5, y = i*40, width=80, height=40, anchor=NW)
            self.buttons.append(button)

        next_button = Button(self.ws, text="Next Image", command=self.next_image)
        next_button.place(x = self.target_size[0]*0.5, y = 2 * self.number_of_colors * 40, width=80, height=40, anchor=NW)

        self.load_image(self.image_files[0])
        self.file_counter = 0

        # Start the Tkinter main loop
        self.ws.mainloop()


matte_picker = MattePicker()