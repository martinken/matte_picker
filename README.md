## [matte_picker - a simple python program to help matte artwork for digital frames]


Introduction
============

matte_picker is a simple python program that takes a directory of artwork
and for each image in the directory it will display the image along with
suggested matte colors. You can click on the suggested colors to see what they look like on the artwork
and then when happy, select next image to save the current image and 
move to the next image. When all the images are matted the program exits.

Matted images are resized to fit the target size and matted
with you selected color andwritten to an output_images folder.

Suggeted colors are determine via k-means clustering on a reduced
resolution image. The means are then have their luminance adjusted
light and dark to make up a pair of suggested matte colors for each
of the means. So with 8 means the program will display 16 suggested
matte colors.

Example
============

edit the settings in matte_picker if you want to change the output resolution etc

cd to a directory of artwork and run it as python matte_picker.py

