# matte_picker - Matte and Resize Artwork for Digital Frames

## Introduction

matte_picker is a powerful Python program that mattes and resizes artwork for digital frames. It provides an intuitive interface with suggested matte colors, navigation controls, and flexible input/output directory management.

For each image, suggested colors are determined via k-means clustering on a reduced resolution image. The means then have their luminance adjusted to create light and dark pairs of suggested matte colors. With 8 means, the program displays 16 suggested matte colors.

Matted images are automatically resized to fit the target size, matted with your selected color, and saved to the output directory.

## New Features

### 🎨 Enhanced User Interface
- **Menu System**: Full menu bar with File and Navigation menus
- **Keyboard Shortcuts**: Intuitive keyboard navigation
- **Window Title**: Shows current image and position (e.g., "image.jpg (3/10)")
- **Dynamic Menu State**: Menu items enable/disable based on context

### 📁 Flexible Directory Management
- **Command Line Arguments**: Specify input/output directories via command line
- **Folder Selection Dialog**: Interactive folder selection when no arguments provided
- **Open Folder**: Load images from different directories without restarting

### ⌨️ Keyboard Shortcuts
- **← (Left Arrow)**: Previous Image
- **→ (Right Arrow)**: Next Image
- **Page Up/Page Down**: Previous/Next Image
- **Backspace**: Previous Image
- **Ctrl+O**: Open Folder
- **Ctrl+Q**: Exit Application

## Command Line Usage

```bash
# With both input and output directories specified
python matte_picker.py --input_dir "path/to/images" --output_dir "path/to/output"
python matte_picker.py -i "path/to/images" -o "path/to/output"

# With only input directory (output will be input_dir/output_images)
python matte_picker.py --input_dir "path/to/images"
python matte_picker.py -i "path/to/images"

# Without arguments (shows folder selection dialog)
python matte_picker.py

# Help message
python matte_picker.py --help
```

## Menu Navigation

### File Menu
- **Open Folder... (Ctrl+O)**: Open a different directory of images
- **Exit (Ctrl+Q)**: Close the application

### Navigation Menu
- **Previous Image (Left Arrow)**: Go to the previous image
- **Next Image (Right Arrow)**: Go to the next image (saves current image)

## Configuration

The program can be configured by modifying the settings in the `__init__` method:

```python
# Configuration
self.target_size = (3840, 2160)     # desired final size with matting
self.minimum_border = 120           # Minimum border width in pixels
self.number_of_colors = 8           # Number of colors to extract
```

## Usage

1. **Run the program**:
   ```bash
   python matte_picker.py
   ```

2. **Select a folder** containing your images (if not specified via command line)

3. **Choose a matte color** by clicking on one of the suggested color patches

4. **Navigate through images** using:
   - Mouse: Click "Next Image" button or use the Navigation menu
   - Keyboard: Use ← → arrow keys or Page Up/Page Down

5. **Change folders** at any time using File → Open Folder or Ctrl+O

6. **Exit** when finished using File → Exit or Ctrl+Q

## Example

![Screenshot](https://github.com/user-attachments/assets/f192a85f-6626-40a5-8cc4-9a0f748d7b67)

## Tips

- Use keyboard shortcuts for faster navigation
- The window title shows your current position in the image sequence
- Previous Image is disabled when you're on the first image
- All processed images are automatically saved with their original filenames
- The output directory is automatically created if it doesn't exist

## Backward Compatibility

All changes are fully backward compatible. The program works exactly as before but now provides enhanced functionality and a better user experience.
