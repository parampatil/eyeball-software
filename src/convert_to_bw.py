from PIL import Image
import os

def convert_image_to_bw(image_path):
    color_image = Image.open(image_path)
    bw_image = color_image.convert("L")  # Convert to grayscale
    return bw_image

def process_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            bw_image = convert_image_to_bw(input_path)
            bw_image.save(output_path)

    return output_folder
