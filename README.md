# EyeballProject

EyeballProject is a GUI application designed to simulate how the human eye perceives images. The application allows users to input images and apply various visual transformations, such as adding blur or changing colors, to mimic the perception of the human eyeball.

## Features

- **Load Images**: Select a folder containing images to load into the application.
- **Preview Images**: View the input images and the processed output images in separate tabs.
- **Image Transformation**:
  - Convert images to black and white.
  - Apply color filters (Red, Green, Blue) to images.
  - Add Gaussian blur to images.
- **Advanced Processing Options**:
  - Adjust input image resolution.
  - Set fovea location and radius to simulate focus.
  - Simulate peripheral vision effects, such as active cone cells and rod cells.
  - Apply Gaussian blur and grayscale effects to the peripheral vision.
  - Simulate retinal warp.
  - Choose between single-eye and dual-eye vision.
  - Select between static and dynamic fovea types.
- **Save Processed Images**: Save the transformed images to a specified directory.

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python libraries:
  - PyQt6
  - PIL (Pillow)
  - NumPy

### Usage

- Load Images: Click on "Load Images" and select a folder containing your images.
- Set Parameters: Adjust the processing parameters in the sidebar according to your needs.
- Run Model: Click on "Run Model" to apply the selected transformations to your images.
- Preview: View the transformed images in the "Processed Images" tab.
- Save Images: Click on "Save Images" to save the processed images to a directory of your choice.

### To-Do
- [ ] Merge Client's Script: Integrate the client's existing script for additional processing.
- [ ] Add UI Kit: Implement a UI kit for consistent design and improved user experience.
- [ ] Add Prompts for Status: Provide real-time status updates to the user during image processing.
- [ ] Add Progress Bar: Display a progress bar to indicate the completion status of the image processing tasks.
- [ ] Add Multi-Thread Support: Improve performance by implementing multi-threading for concurrent processing.