import streamlit as st
import os
from PIL import Image
from convert_to_bw import process_images

# Function to load images from a folder or list of files
def load_images_from_folder(folder, start_idx=0, num_images=10):
    images = []
    filenames = os.listdir(folder)
    for filename in filenames[start_idx:start_idx + num_images]:
        img = Image.open(os.path.join(folder, filename))
        if img is not None:
            images.append((filename, img))
    return images, len(filenames) > start_idx + num_images

# Function to load images from uploaded files
def load_images_from_files(files):
    images = []
    for file in files:
        img = Image.open(file)
        if img is not None:
            images.append((file.name, img))
    return images

# Function to save images to a new folder
def save_images_to_folder(images, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename, img in images:
        img.save(os.path.join(output_folder, filename))

st.set_page_config(page_title="Image Processing App", layout="wide")

# Inspector side panel
st.sidebar.header("Inspector Panel")
radio_input = st.sidebar.radio("Radio Input", ["Option 1", "Option 2", "Option 3"])
slider_input = st.sidebar.slider("Slider Input", 0, 100, 50)
number_input = st.sidebar.number_input("Number Input", min_value=0, max_value=100, value=10)
text_input = st.sidebar.text_input("Text Input", value="Enter text here")

# Tabs for the three-step process
tabs = st.tabs(["Getting Inputs", "Preview", "Output"])

with tabs[0]:
    st.title("Step 1: Getting Inputs")

    # File uploader for folder or multiple files
    uploaded_files = st.file_uploader("Upload images (multiple files allowed)", type=["png", "jpg", "jpeg"], accept_multiple_files=True  )
    folder = st.text_input("Or enter a folder path with images:")
    
    if uploaded_files or folder:
        if uploaded_files:
            images = load_images_from_files(uploaded_files)
        elif folder:
            if os.path.exists(folder):
                start_idx = st.session_state.get('start_idx', 0)
                num_images = st.session_state.get('num_images', 10)
                images, more_images = load_images_from_folder(folder, start_idx, num_images)
            else:
                st.error("Folder does not exist.")
        st.session_state['images'] = images
        st.session_state['folder'] = folder
        st.session_state['uploaded_files'] = uploaded_files
    

with tabs[1]:
    st.title("Step 2: Preview")

    if 'images' in st.session_state:
        images = st.session_state['images']
        
        # Display images in a grid
        st.subheader("Image Preview")
        cols = st.columns(5)
        for i, (filename, img) in enumerate(images):
            with cols[i % 5]:
                st.image(img, caption=filename, use_column_width=True)
        
        # Display images in a carousel (simple implementation)
        st.subheader("Image Carousel")
        for filename, img in images:
            st.image(img, caption=filename, use_column_width=True)
        
        if 'folder' in st.session_state and st.session_state['folder']:
            if len(os.listdir(st.session_state['folder'])) > len(images):
                if st.button("Load More"):
                    st.session_state['start_idx'] += 10
                    images, more_images = load_images_from_folder(st.session_state['folder'], st.session_state['start_idx'], 10)
                    st.session_state['images'].extend(images)
                    st.rerun()
    else:
        st.warning("No images uploaded or selected.")

    if st.button("Next Step"):
        st.session_state['active_tab'] = "Output"
        st.rerun()

with tabs[2]:
    st.title("Step 3: Output")

    if 'images' in st.session_state:
        if st.button("Run Model"):
            output_folder = "processed_images"
            if 'folder' in st.session_state and st.session_state['folder']:
                process_images(st.session_state['folder'], output_folder)
            elif 'uploaded_files' in st.session_state:
                os.makedirs(output_folder, exist_ok=True)
                for filename, img in st.session_state['images']:
                    img.save(os.path.join(output_folder, filename))
                process_images(output_folder, output_folder)
            st.session_state['output_folder'] = output_folder
            st.rerun()

        output_folder = st.session_state.get('output_folder', None)
        if output_folder is not None:
            st.success("Model processing complete!")

            # Display processed images
            st.subheader("Processed Images")
            images, _ = load_images_from_folder(output_folder)
            for filename, img in images:
                st.image(img, caption=f"Processed: {filename}", use_column_width=True)

            if st.button("Save to Directory"):
                save_images_to_folder(images, "processed_images")
                st.success("Images saved to processed_images directory.")
        else:
            st.warning("No processed images to display.")
    else:
        st.warning("No images to process.")

    if st.button("Back to Preview"):
        st.session_state['active_tab'] = "Preview"
        st.rerun()
