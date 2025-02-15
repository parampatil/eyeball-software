import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.transform import resize
from tqdm import tqdm

class ArtificialRetina:
    '''
    [args]:
    image - Input RGB image path,
    P - size of the image, 
    fovea_center - (x,y) coordinates of the fovea,
    fovea_radius - radius r of the fovea,
    peripheral_active_cones - x% of active cones (color cells) on the peripheral region, 
    fovea_active_rods - x% of active rods (non-color cells) on the fovea,
    peripheral_gaussianBlur - enable/disable Gaussian Blur on the peripheral region,
    peripheral_gaussianBlur_kernal - Gaussian Blur kernal size,
    peripheral_grayscale - apply grayscale on the peripheral region if True,
    verbose - emable/disable to display selected settings,
    video - True if input is a video,
    save_output - save the output image/video to drive,
    output_dir - dir to save the output image/video,
    
    '''
    def __init__(self,
                #  image=None,
                 P=0,
                 fovea_center=(0,0),
                 fovea_radius=0,
                 peripheral_active_cones=0,
                 fovea_active_rods=0,
                 peripheral_gaussianBlur=True,
                 peripheral_gaussianBlur_kernal=(21,21),
                 peripheral_grayscale=True,
                 foveation_type='static',
                 dynamic_foveation_grid_size=(10,10),
                 grad_blur=(121,121),
                 visual_clutter=True,
                 clutter_intensity=0.5,
                 cortical_magnifi=False,
                 magnifi_strength=0.5,
                 magnifi_radius=0.3,
                #  display_output=False,
                #  verbose=True,
                #  save_output=False,
                #  output_dir=None,
                ):
        # self.image = image
        self.P = P
        self.foveation_type = foveation_type
        self.dynamic_foveation_grid_size = dynamic_foveation_grid_size
        self.fovea_center = fovea_center
        self.fovea_radius = fovea_radius
        self.peripheral_active_cones = peripheral_active_cones
        self.fovea_active_rods = fovea_active_rods
        self.peripheral_gaussianBlur = peripheral_gaussianBlur
        self.peripheral_gaussianBlur_kernal = peripheral_gaussianBlur_kernal
        self.grad_blur = grad_blur
        self.visual_clutter = visual_clutter
        self.clutter_intensity = clutter_intensity
        self.peripheral_grayscale = peripheral_grayscale
        self.cortical_magnifi = cortical_magnifi
        self.magnifi_strength = magnifi_strength
        self.magnifi_radius = magnifi_radius
        # self.display_output = display_output
        # self.verbose = verbose
        # self.save_output = save_output
        # self.output_dir = output_dir

    def apply(self, image_path: str, next_frame_path: str) -> np.array:
        # This is the entry point for the class

        # check if all the variables are properly assigned and valid
        self.checks()


        # open and pre-process RGB image
        preprocessed_image = self.preprocess(image_path)


        # dynamically adjust the fovea location based on optic flow magnitude
        if self.foveation_type == 'dynamic':
            # pre-process the next_frame
            next_frame_proc = self.preprocess(next_frame_path)

            # pass t and t+1 frames to get coordinates for dynamic foveation
            fovea_x, fovea_y = self.dynamic_fovea(prev_frame=preprocessed_image, current_frame=next_frame_proc, grid_size=self.dynamic_foveation_grid_size)
            
            # update self.center
            self.fovea_center = (fovea_x,fovea_y)
    

        # create retina_filter and generate parts of the retina
        self.fovea, self.peripheral_mask = self.create_retina_filter()
        # apply retinal filter on image
        self.retina_image = self.apply_retina_filter(preprocessed_image)

        # activate cones and rods in peripheral and fovea respectively
        # randomly select x% of pixels in the fovea and make them grayscale
        self.fovea_selected_indices = self.__select_random_pixels(
            percentage=self.fovea_active_rods, 
            mask=self.fovea
        )

        self.__apply_random_pixel_effect(
            preprocessed_image=preprocessed_image,
            retina_image=self.retina_image, 
            selected_indices=self.fovea_selected_indices, 
            effect='grayscale'
        )

        # randomly select y% of pixels in the peripheral and remove grayscale effect
        self.peripheral_selected_indices = self.__select_random_pixels(
            percentage=self.peripheral_active_cones, 
            mask=self.peripheral_mask
        )

        self.__apply_random_pixel_effect(
            preprocessed_image=preprocessed_image,
            retina_image=self.retina_image,
            selected_indices=self.peripheral_selected_indices,
            effect='color'
        )

        if self.cortical_magnifi == True:
            self.retina_image = self.cortical_magnification(
                image=self.retina_image, 
                center=self.fovea_center, 
                strength=self.magnifi_strength,
                radius=self.magnifi_radius
            )
        
        return self.retina_image.astype('uint16')
    
    def checks(self) -> None:
        # check if all the variables are properly assigned  and valid

        if self.fovea_radius <= 0:
            raise ValueError("Fovea radius must be greater than 0.")
        if self.foveation_type not in ['dynamic', 'static']:
            raise ValueError("Unsupported foveation type. Choose from ['dynamic', 'static']")

    def preprocess(self, image_path: str = None) -> np.array:
        # pre-process the raw RGB image before mapping on the retina filter

        if os.path.exists(image_path):
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Resize the image to match the filter size (PxP)
            preprocessed_image = cv2.resize(image_rgb, (self.P, self.P))
            return preprocessed_image
        else:
            return None
        

    def create_retina_filter(self) -> tuple:
        # create a 2D mask for the circular fovea region
        mask = np.zeros((self.P, self.P), dtype=np.float32) # changed from Uint8 for smooth gradient effect

        # plot the fovea on the 2D mask
        '''
        args:
        mask - background on which the circle will be created
        center - coordinates for the circle
        radius - radius of the circle
        (1,1,1) - value inside the circle
        -1 - outline of the circle, -1 means no outline
        '''         
        
        fovea = cv2.circle(mask, self.fovea_center, self.fovea_radius, (1,1,1), -1)

        # create mask for the peripheral region of the retina
        peripheral_mask = cv2.bitwise_not(fovea)

        return fovea, peripheral_mask
    

    def apply_retina_filter(self, preprocessed_image: np.array) -> np.array:
 
        # Initialize `img` with the original image
        img = preprocessed_image.copy() # ? Why did you use image.copy() here and np.copy(image) in the radial_pixel_distortion function?
        
        # define kernel
        ker = self.grad_blur if self.peripheral_gaussianBlur else (1, 1)

        # Initialize the mask with the original fovea
        mask = cv2.GaussianBlur(self.fovea, ker, 0)
        mask = np.dstack([mask] * 3)


        # Apply Gaussian blur to the entire image if enabled
        if self.peripheral_gaussianBlur:
            img = cv2.GaussianBlur(img, self.peripheral_gaussianBlur_kernal, 0)

        # apply visual clutter to the entire image
        if self.visual_clutter == True:
            img = self.radial_pixel_distortion(image=img, distortion_intensity=self.clutter_intensity)
        
        # Convert the entire image to grayscale if enabled
        if self.peripheral_grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img = cv2.merge([img] * 3)  # Convert to 3-channel grayscale
        
        # Combine the foveal and peripheral regions
        combined_image = preprocessed_image * mask + img * (1 - mask)

        return combined_image


    # Function to calculate optical flow and dynamically determine new fovea position
    def dynamic_fovea(self, prev_frame=None, current_frame=None, grid_size=(10, 10)) -> tuple:
        # Convert frames to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        # Calculate optical flow (only accepts single channel images) at timestamps t and t+1
        flow = cv2.calcOpticalFlowFarneback(prev_gray, current_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        
        # Calculate magnitude and angle of 2D vectors (flow vector in this case)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        # Initialize grid for average magnitude calculation
        h, w = mag.shape
        grid_h, grid_w = grid_size
        avg_magnitude = np.zeros((grid_h, grid_w))
       
        # Calculate average magnitude for each grid cell
        for i in range(grid_h):
            for j in range(grid_w):
                y0, y1 = i * h // grid_h, (i + 1) * h // grid_h
                x0, x1 = j * w // grid_w, (j + 1) * w // grid_w
    
                # after knowing what pixels are in each cell, we take the average of those pixels
                avg_magnitude[i, j] = np.mean(mag[y0:y1, x0:x1])
    
        max_idx = np.unravel_index(np.argmax(avg_magnitude), avg_magnitude.shape)
        fovea_y, fovea_x = max_idx[0] * h // grid_h + h // (2 * grid_h), max_idx[1] * w // grid_w + w // (2 * grid_w)
        
        return fovea_x, fovea_y


    def radial_pixel_distortion(self, image, max_distortion=10, distortion_intensity=1.0) -> np.array:
        rows, cols, _ = image.shape
        distorted_image = np.copy(image)
    
        adjusted_max_distortion = max_distortion * distortion_intensity
    
        for y in range(rows):
            for x in range(cols):
                # Generate a random radius and angle for radial distortion
                radius = np.random.uniform(0, adjusted_max_distortion)
                angle = np.random.uniform(0, 2 * np.pi)
    
                # Convert polar to Cartesian
                dx = int(radius * np.cos(angle))
                dy = int(radius * np.sin(angle))
    
                # Calculate new pixel location
                x_new = np.clip(x + dx, 0, cols - 1)
                y_new = np.clip(y + dy, 0, rows - 1)
    
                # Set the new pixel value
                distorted_image[y, x] = image[y_new, x_new]
    
        return distorted_image


    # private function to randomly select x% of cones and rods cells   
    def __select_random_pixels(self, percentage, mask) -> np.array:
        # determine the number of pixels to select based on the percentage
        num_pixels = int(percentage / 100 * np.count_nonzero(mask)) # total pixels = HxW

        # get the indices of non-zero pixels in the image mask
        nonzero_indices = np.transpose(np.nonzero(mask))

        # randomly select pixel coordinates
        random_indices = np.random.choice(len(nonzero_indices), num_pixels, replace=False)
        selected_indices = nonzero_indices[random_indices]

        return selected_indices
    
    # private function to activate rods and cones at specified coordinates
    def __apply_random_pixel_effect(self, preprocessed_image: np.array, retina_image: np.array, selected_indices: np.array, effect: str) -> None:
        # apply the specified effect to the randomly selected pixels
        for y, x in selected_indices:
            if effect == 'grayscale':
                retina_image[y, x] = np.mean(retina_image[y, x])
            elif effect == 'color':
                retina_image[y, x] = preprocessed_image[y, x]
            else:
                raise ValueError("Unsupported effect type. Supported types are 'grayscale' and 'color'.")
        
    
    def cortical_magnification(self, image, center, strength=0.5, radius=0.3):
        
        height, width = image.shape[:2]
        min_dim = min(height, width) # ? Not used
        
        # Normalize coordinates to [-1, 1] space
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        xv, yv = np.meshgrid(x, y)
        
        # Normalize the focal center to [-1, 1]
        center_x = (center[0] / width) * 2 - 1
        center_y = (center[1] / height) * 2 - 1
        
        # Shift grid based on the focal point
        xv -= center_x
        yv -= center_y
        
        # Calculate distance from the center
        distance = np.sqrt(xv**2 + yv**2)
        distance = np.clip(distance, 1e-6, 1.0)
        
        # Define outward magnification using a smooth falloff function
        falloff = np.exp(-((distance / radius) ** 2))
        magnification = 1 + strength * falloff
        
        # Invert the distortion effect (scale outward)
        xv = xv / magnification + center_x
        yv = yv / magnification + center_y
        
        # Map back to pixel coordinates
        map_x = ((xv + 1) * 0.5 * width).astype(np.float32)
        map_y = ((yv + 1) * 0.5 * height).astype(np.float32)
        
        # Remap image using the distortion map
        magnified_image = cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR)
        
        return magnified_image


# # DRIVER CODE - 
# P = 256 # output image resolution
# center = (P // 2 + 40 , P // 2)  # Center of the fovea region

# # creating instance - 
# retina = ArtificialRetina(
#         #  image='D:\Work\Justin Wood - IUB\Lalit Pandey\EyeBall\Dataset\Large Dataset\output_0.png',
#          P=P,
#          foveation_type='dynamic',
#          dynamic_foveation_grid_size=(5,5),
#          fovea_center=center,
#          fovea_radius=50,
#          peripheral_active_cones=0,
#          fovea_active_rods=0,
#          peripheral_gaussianBlur=True, # always keep this True
#          peripheral_gaussianBlur_kernal=(1,1),
#          grad_blur=(91,91),
#          visual_clutter=True,
#          clutter_intensity=0.5,
#          peripheral_grayscale=True,
#          cortical_magnifi=True,
#          magnifi_strength=2.5,
#          magnifi_radius=0.4,
#         #  verbose=False,
#         #  display_output=True,
#         #  save_output=False,
#         #  output_dir=None,
# )
# proc_image = retina.apply(image_path='D:\Work\Justin Wood - IUB\Lalit Pandey\EyeBall\Dataset\Large Dataset\output_0.png', next_frame_path='D:\Work\Justin Wood - IUB\Lalit Pandey\EyeBall\Dataset\Large Dataset\output_100.png')
#  # Display the image using matplotlib
# plt.imshow(proc_image.astype(np.uint8))
# #plt.title('Retina Filter Applied')
# plt.axis('off')
# plt.show()