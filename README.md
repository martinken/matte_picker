## [matte_picker - matte and resize artwork for digital frames]


Introduction
============

matte_picker is a simple python program that mattes and resizes artwork
for a digital frame. For each image in the directory itis run in it will 
display the image along with suggested matte colors. You can click on the 
suggested colors to see what they look like on the artwork
and then when happy, click next image to save the current image and 
move to the next image. When all the images are matted the program exits.

Matted images are resized to fit the target size, matted
with your selected color, and written to the output_images folder.

For each image, suggested colors are determined via k-means clustering on a reduced
resolution image. The means then have their luminance adjusted
light and dark to make a pair of suggested matte colors for each
of the means. With 8 means the program will display 16 suggested
matte colors.

Example
============

edit the settings in matte_picker if you want to change the output resolution etc
```
        # Configuration
        self.input_dir = '.'                # Directory containing images
        self.output_dir = './output_images' # Directory to save processed images
        self.target_size = (3840, 2160)     # desired final size with matting
        self.minimum_border = 120           # Minimum border width in pixels
        self.number_of_colors = 8           # Number of colors to extract
```

cd to a directory of artwork and run it as python matte_picker.py

![Screenshot](https://github.com/user-attachments/assets/f192a85f-6626-40a5-8cc4-9a0f748d7b67)
