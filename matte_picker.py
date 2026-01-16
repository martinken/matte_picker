import os
import sys
from tkinter import Tk, Canvas, Button, Menu, messagebox, NW, DISABLED, NORMAL
from tkinter import filedialog
import PIL
from PIL import Image, ImageCms, ImageTk
from functools import partial
import cv2
import numpy as np
import argparse


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

def select_input_directory():
    """Display a folder selection dialog to pick input directory"""
    root = Tk()
    root.withdraw()  # Hide the main window
    input_dir = filedialog.askdirectory(title="Select Input Directory")
    root.destroy()
    return input_dir

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
        output_path = os.path.join(self.output_dir, os.path.basename(self.image_files[self.file_counter]))
        self.img_bordered.save(output_path,'jpeg',quality=95, optimize=True)

        self.file_counter += 1
        if self.file_counter == len(self.image_files):
            self.ws.destroy()
        else:
            self.load_image(self.image_files[self.file_counter])
            self.update_menu_state()

    def previous_image(self):
        if self.file_counter > 0:
            self.file_counter -= 1
            self.load_image(self.image_files[self.file_counter])
            self.update_menu_state()

    def open_folder(self):
        """Open a new folder and reload images"""
        input_dir = select_input_directory()
        if input_dir:
            self.input_dir = input_dir
            self.output_dir = os.path.join(self.input_dir, 'output_images')
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Reload image files
            self.image_files = []
            for filename in os.listdir(self.input_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    img_path = os.path.join(self.input_dir, filename)
                    self.image_files.append(img_path)
            
            if self.image_files:
                self.file_counter = 0
                self.load_image(self.image_files[self.file_counter])
                self.update_menu_state()
            else:
                # Show message if no images found
                messagebox.showinfo("No Images", "No image files found in the selected directory.")

    def create_menu(self):
        """Create the menu bar with File and Navigation menus"""
        menubar = Menu(self.ws)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Folder...", command=self.open_folder, accelerator='Ctrl+O')
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.ws.destroy, accelerator='Ctrl+Q')
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Navigation menu
        nav_menu = Menu(menubar, tearoff=0)
        nav_menu.add_command(label="Previous Image", command=self.previous_image, state=DISABLED, accelerator='Left Arrow')
        nav_menu.add_command(label="Next Image", command=self.next_image, accelerator='Right Arrow')
        menubar.add_cascade(label="Navigation", menu=nav_menu)
        
        self.ws.config(menu=menubar)
        
        # Store menu references for later updates
        self.file_menu = file_menu
        self.nav_menu = nav_menu
        self.prev_menu_index = 0  # Index of Previous Image menu item

    def update_menu_state(self):
        """Update the state of menu items based on current position"""
        # Enable/disable Previous Image menu item
        if self.file_counter > 0:
            self.nav_menu.entryconfig(self.prev_menu_index, state=NORMAL)
        else:
            self.nav_menu.entryconfig(self.prev_menu_index, state=DISABLED)
        
        # Update window title to show current image
        if self.image_files:
            current_image_name = os.path.basename(self.image_files[self.file_counter])
            self.ws.title(f'Matte Picker - {current_image_name} ({self.file_counter + 1}/{len(self.image_files)})')

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for navigation"""
        # Bind arrow keys for navigation
        self.ws.bind('<Left>', lambda event: self.previous_image())
        self.ws.bind('<Right>', lambda event: self.next_image())
        
        # Bind additional shortcuts
        self.ws.bind('<Prior>', lambda event: self.previous_image())  # Page Up
        self.ws.bind('<Next>', lambda event: self.next_image())      # Page Down
        self.ws.bind('<BackSpace>', lambda event: self.previous_image())
        
        # Bind Ctrl+O for Open Folder
        self.ws.bind('<Control-o>', lambda event: self.open_folder())
        self.ws.bind('<Control-O>', lambda event: self.open_folder())
        
        # Bind Ctrl+Q for Exit
        self.ws.bind('<Control-q>', lambda event: self.ws.destroy())
        self.ws.bind('<Control-Q>', lambda event: self.ws.destroy())
        
        # Note: Accelerators are already set in the menu creation

    def __init__(self, input_dir=None, output_dir=None):
        # Configuration
        if input_dir is None:
            self.input_dir = select_input_directory()
            if not self.input_dir:  # User cancelled the dialog
                sys.exit(0)
        else:
            self.input_dir = input_dir
        
        # Set output directory - use explicit if provided, otherwise create subdirectory
        if output_dir is None:
            self.output_dir = os.path.join(self.input_dir, 'output_images')
        else:
            self.output_dir = output_dir
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
        
        # Create menu bar after initialization
        self.create_menu()
        
        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Start the Tkinter main loop
        self.ws.mainloop()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Matte Picker - Add borders to images')
    parser.add_argument('--input_dir', '-i', type=str, help='Input directory containing images')
    parser.add_argument('--output_dir', '-o', type=str, help='Output directory for processed images')
    args = parser.parse_args()
    
    # Create MattePicker instance with optional input directory and output directory
    matte_picker = MattePicker(args.input_dir, args.output_dir)

if __name__ == '__main__':
    main()