import cv2, os
import numpy as np

'''
for retinal warp, cite -
https://github.com/dicarlolab/retinawarp/
'''
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import sys
from skimage.transform import resize
# retinal warp (cortical magnification)
sys.path.append("/home/lpandey/retinawarp/")
# foveated texture (peripheral vision)
sys.path.append("/home/lpandey/Baby_Research/NeuroFovea_PyTorch/")
# from retina.retina import warp_image
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
    peripheral_gaussianBlur_sigma - Blur intensity, if 0 then automatically calculated from kernal size,
    peripheral_grayscale - apply grayscale on the peripheral region if True,
    verbose - emable/disable to display selected settings,
    video - True if input is a video,
    save_output - save the output image/video to drive,
    output_dir - dir to save the output image/video,
    
    '''
    def __init__(self,
                 #image=None,
                 P=0,
                 fovea_center=0,
                 fovea_radius=0,
                 peripheral_active_cones=0,
                 fovea_active_rods=0,
                 peripheral_gaussianBlur=True,
                 peripheral_gaussianBlur_kernal=(21,21),
                 peripheral_gaussianBlur_sigma=0,
                 peripheral_grayscale=True,
                 foveation_type='dynamic',
                 dynamic_foveation_grid_size=(10,10),
                 retinal_warp=False,
                 display_output=False,
                 verbose=False,
                 video=None,
                 save_output=False,
                 output_dir=None,
                ):
        #self.image = image
        self.P = P
        self.foveation_type = foveation_type
        self.dynamic_foveation_grid_size = dynamic_foveation_grid_size
        self.fovea_center = fovea_center
        self.fovea_radius = fovea_radius
        self.peripheral_active_cones = peripheral_active_cones
        self.fovea_active_rods = fovea_active_rods
        self.peripheral_gaussianBlur = peripheral_gaussianBlur
        self.peripheral_gaussianBlur_kernal = peripheral_gaussianBlur_kernal
        self.peripheral_gaussianBlur_sigma = peripheral_gaussianBlur_sigma
        self.peripheral_grayscale = peripheral_grayscale
        self.retinal_warp = retinal_warp
        self.display_output = display_output
        self.verbose = verbose
        self.video = video
        self.save_output = save_output
        self.output_dir = output_dir

        # check for errors
        # self.checks()
                  
        # # open and pre-process RGB image
        # self.preprocessed_image = self.preprocess()

        # # dynamically adjust the fovea location based on optic flow magnitude
        # if self.foveation_type == 'dynamic':
        #     # get next frame (t+1)
        #     self.next_frame = self.get_next_frame()

        #     # pre-process the next_frame
        #     self.next_frame_proc = self.preprocess(img=self.next_frame)

        #     # pass t and t+1 frames to get coordinates for dynamic foveation
        #     fovea_x, fovea_y = self.dynamic_fovea(prev_frame=self.preprocessed_image, current_frame=self.next_frame_proc, grid_size=self.dynamic_foveation_grid_size)
            
        #     # update self.center
        #     self.fovea_center = (fovea_x,fovea_y)

        # # display selected settings
        # if self.verbose:
        #     self.display_info()

        # # create retina_filter and generate parts of the retina
        # self.filter_canvas, self.fovea, self.peripheral_mask = self.create_retina_filter()
        # # apply retinal filter on image
        # self.retina_image = self.apply_retina_filter()

        # # activate cones and rods in peripheral and fovea respectively
        # # randomly select x% of pixels in the fovea and make them grayscale
        # self.fovea_selected_indices = self.__select_random_pixels(
        #     percentage=self.fovea_active_rods, 
        #     mask=self.fovea)

        # self.__apply_random_pixel_effect(
        #     retina_image=self.retina_image, 
        #     selected_indices=self.fovea_selected_indices, effect='grayscale')

        # if self.verbose:
        #     print("[INFO] {}% rods turned active in the fovea".format(self.fovea_active_rods))

        # # randomly select y% of pixels in the peripheral and remove grayscale effect
        # self.peripheral_selected_indices = self.__select_random_pixels(
        #     percentage=self.peripheral_active_cones, 
        #     mask=self.peripheral_mask)

        # self.__apply_random_pixel_effect(
        #     retina_image=self.retina_image, 
        #     selected_indices=self.peripheral_selected_indices, effect='color')

        # if self.verbose:
        #     print("[INFO] {}% cones turned active in the peripheral".format(self.peripheral_active_cones))

        # if self.retinal_warp == True:
        #     self.ret_warp = self.apply_retinalWarp()
        
        # # display the output image from the artificial retina
        # if self.display_output:
        #     self.output_image()

    def apply(self, image_path: str, next_frame_path: str) -> np.array:
        preprocessed_image = self.preprocess(image_path)

        # dynamically adjust the fovea location based on optic flow magnitude
        if self.foveation_type == 'dynamic':
            # get next frame (t+1)
            # self.next_frame = self.get_next_frame(image_path)

            # pre-process the next_frame
            next_frame_proc = self.preprocess(next_frame_path)
            if next_frame_proc is not None:

                # pass t and t+1 frames to get coordinates for dynamic foveation
                fovea_x, fovea_y = self.dynamic_fovea(prev_frame=preprocessed_image, current_frame=next_frame_proc, grid_size=self.dynamic_foveation_grid_size)
                
                # update self.center
                self.fovea_center = (fovea_x,fovea_y)

        # display selected settings
        if self.verbose:
            self.display_info()

        # create retina_filter and generate parts of the retina
        self.filter_canvas, self.fovea, self.peripheral_mask = self.create_retina_filter()
        # apply retinal filter on image
        retina_image = self.apply_retina_filter(preprocessed_image)

        # activate cones and rods in peripheral and fovea respectively
        # randomly select x% of pixels in the fovea and make them grayscale
        self.fovea_selected_indices = self.__select_random_pixels(
            percentage=self.fovea_active_rods, 
            mask=self.fovea)

        self.__apply_random_pixel_effect(
            retina_image=retina_image, original_image=preprocessed_image, 
            selected_indices=self.fovea_selected_indices, effect='grayscale')

        if self.verbose:
            print("[INFO] {}% rods turned active in the fovea".format(self.fovea_active_rods))

        # randomly select y% of pixels in the peripheral and remove grayscale effect
        self.peripheral_selected_indices = self.__select_random_pixels(
            percentage=self.peripheral_active_cones, 
            mask=self.peripheral_mask)

        self.__apply_random_pixel_effect(
            retina_image=retina_image, original_image=preprocessed_image,
            selected_indices=self.peripheral_selected_indices, effect='color')

        if self.verbose:
            print("[INFO] {}% cones turned active in the peripheral".format(self.peripheral_active_cones))

        if self.retinal_warp == True:
            retina_image = self.apply_retinalWarp(retina_image)*255
        
        return retina_image.astype('uint16')
    # check if all the variables are properly assigned
    def checks(self,):
        #if self.image is None and self.video is None:
        #    raise ValueError("Image or video must be provided as input.")
        if self.fovea_radius <= 0:
            raise ValueError("Fovea radius must be greater than 0.")
        if self.output_dir is not None and not isinstance(self.output_dir, str):
            raise TypeError("output_dir must be a string.")
        if self.save_output is True and self.output_dir is None:
            raise ValueError("Output dir not specified.")
        if self.foveation_type not in ['dynamic', 'static']:
            raise ValueError("Unsupported foveation type. Choose from ['dynamic', 'static']")

    # pre-process the raw RGB image before mapping on the retina filter
    def preprocess(self, image_path: str = None):
        if os.path.exists(image_path):
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Resize the image to match the filter size (PxP)
            preprocessed_image = cv2.resize(image_rgb, (self.P, self.P))
            return preprocessed_image
        else:
            return None
            
    def display_info(self):
        print(f'''
        Image Information:
        -----------------
        Image size: {self.P}x{self.P}
        
        Fovea Information:
        ------------------
        Fovea type: {self.foveation_type}
        Dynamic fovea grid size: {self.dynamic_foveation_grid_size}
        Fovea center: {self.fovea_center}
        Fovea radius: {self.fovea_radius}
        Fovea active rods: {self.fovea_active_rods}%
        
        Peripheral Information:
        -----------------------
        Peripheral active cones: {self.peripheral_active_cones}%
        Peripheral Gaussian Blur: {self.peripheral_gaussianBlur}
        Peripheral Gaussian Blur kernel: {self.peripheral_gaussianBlur_kernal}
        Peripheral Gaussian Blur sigma: {self.peripheral_gaussianBlur_sigma}
        Peripheral Grayscale: {self.peripheral_grayscale}
        
        Additional Settings:
        --------------------
        Video input: {self.video is not None}
        Save output: {self.save_output}
        Output directory: {self.output_dir if self.save_output else 'N/A'}
        Retinal Warp: {self.retinal_warp}
        ''')

    # Function to generate the frame at timestamp t+1, given frame at timestamp t
    # Only used when foveation_type=dynamic
    def get_next_frame(self, image_path):    
        # split image path using '_' into two parts from the rightmost side
        base, num_ext = image_path.rsplit('_', 1)
        num, ext = num_ext.split('.')
        next_frame = f"{base}_{int(num) + 1}.{ext}"
        return next_frame

    # Function to calculate optical flow and dynamically determine new fovea position
    def dynamic_fovea(self, prev_frame=None, current_frame=None, grid_size=(10, 10)):
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
    
    def create_retina_filter(self,):
        # create an empty 3D filter canvas of shape (PxPX3)
        filter_canvas = np.zeros((self.P, self.P, 3), dtype=np.uint8)

        # create a 2D mask for the circular fovea region
        mask = np.zeros((self.P, self.P), dtype=np.uint8)

        # plot the fovea on the 2D mask
        '''
        args:
        mask - background on which the circle will be created
        center - coordinates for the circle
        radius - radius of the circle
        (255) - color of the circle
        -1 - outline of the circle, -1 means no outline
        '''
        fovea = cv2.circle(mask, self.fovea_center, self.fovea_radius, (255), -1)

        # create mask for the peripheral region of the retina
        peripheral_mask = cv2.bitwise_not(fovea)
        
        if self.verbose:
            print("[INFO] Retina filter created")

        return filter_canvas, fovea, peripheral_mask

    
    def apply_retina_filter(self, image: np.array):
        '''
        method 1 (in version 0.1)
        the gaussian blur operation is only applied to the peripheral region and the fovea
        region is left as it is i.e., colored and clear. The issue with this method is that
        there is a visible foveal boundary between the peripheral and the fovea region.
        '''
        
        # # create the fovea on the image using fovea mask
        # # perform bitwise_and only for the region passed to mask argument
        # fovea_region = cv2.bitwise_and(self.preprocessed_image, self.preprocessed_image, mask=self.fovea)

        # # similarly, create the peripheral region on the image using the peripheral mask
        # peripheral_region = cv2.bitwise_and(self.preprocessed_image, self.preprocessed_image, mask=self.peripheral_mask)

        # # apply Gaussian Blur to the peripheral region
        # if self.peripheral_gaussianBlur == True:
        #     peripheral_region = cv2.GaussianBlur(
        #         peripheral_region, 
        #         self.peripheral_gaussianBlur_kernal, # kernel size
        #         0 # sigma value
        #     )

        # # apply Grayscale to the peripheral region
        # if self.peripheral_grayscale == True:
        #     peripheral_region = cv2.cvtColor(peripheral_region, cv2.COLOR_RGB2GRAY) # generates 1 channel image
        #     peripheral_region = cv2.merge([peripheral_region]*3) # converting to 3 channel grayscale image

        # # Finally, combine the fovea and the processed peripheral region
        # combined_image = cv2.bitwise_or(fovea_region, peripheral_region)

        # if self.verbose:
        #     print("[INFO] Retina filter applied")

        '''
        method 2 (in version 0.2)
        the foveal boundary issue in versio 0.1 was fixed in this version. Specifically, 
        the gaussian blur is first applied to the entire image, then the image is converted
        to grayscale. Finally, a selective operation is performed where except the fovea region,
        only the peripheral region is swapped in the original image. This creates a smooth 
        transition between the fovea and the peripheral region.
        '''
        sample = image.copy()
        # apply Gaussian blur to the entire image
        if self.peripheral_gaussianBlur == True:
            sample = cv2.GaussianBlur(image, self.peripheral_gaussianBlur_kernal, self.peripheral_gaussianBlur_sigma, borderType=cv2.BORDER_DEFAULT)
        
        # Convert the blurred image to grayscale
        if self.peripheral_grayscale == True:
            sample_gray = cv2.cvtColor(sample, cv2.COLOR_RGB2GRAY)
            # Stack the grayscale image to have the same number of channels as the original image
            sample = cv2.merge([sample_gray, sample_gray, sample_gray])
            
        # Combine the fovea region from the original image with the grayscale blurred peripheral region
        combined_image = image.copy()
        combined_image[self.peripheral_mask == 255] = sample[self.peripheral_mask == 255]

        if self.verbose:
            print("[INFO] Retina filter applied")

        return combined_image

    # private function to randomly select x% of cones and rods cells   
    def __select_random_pixels(self, percentage, mask):
        # determine the number of pixels to select based on the percentage
        num_pixels = int(percentage / 100 * np.count_nonzero(mask)) # total pixels = HxW

        # get the indices of non-zero pixels in the image mask
        nonzero_indices = np.transpose(np.nonzero(mask))

        # randomly select pixel coordinates
        random_indices = np.random.choice(len(nonzero_indices), num_pixels, replace=False)
        selected_indices = nonzero_indices[random_indices]

        return selected_indices

    # private function to activate rods and cones at specified coordinates
    def __apply_random_pixel_effect(self, retina_image, original_image, selected_indices, effect):
        # apply the specified effect to the randomly selected pixels
        for y, x in selected_indices:
            if effect == 'grayscale':
                retina_image[y, x] = np.mean(retina_image[y, x])
            elif effect == 'color':
                retina_image[y, x] = original_image[y, x]
            else:
                raise ValueError("Unsupported effect type. Supported types are 'grayscale' and 'color'.")
    
    def apply_retinalWarp(self, image):
        '''
        for img (224x224 res):
        resize_scale = 4,
        output_size and input_size = 750
        '''
        RESIZE_SCALE = 4
        img = resize(image, np.array(RESIZE_SCALE * np.array(image.shape[:2]), dtype=int))
        ret_img = warp_image(img, output_size=self.P, input_size=self.P)
        return ret_img
            
    # plot/save the image
    def output_image(self,):
        if self.video is None:
            # Display the image using matplotlib
            plt.imshow(self.retina_image)
            #plt.title('Retina Filter Applied')
            plt.axis('off')
            plt.show()

        if self.retinal_warp is True:
            # Display the image using matplotlib
            plt.imshow(self.ret_warp)
            #plt.title('Retina Filter with Retinal Warp Applied')
            plt.axis('off')
            plt.show()
            
    
    # save the output video
    def output_video(self,):
        # TODO: Later
        pass


if __name__ == "__main__":  
    # DRIVER CODE - 
    P = 320 
    center = (P // 2, P // 2)  # Center of the fovea region

    # generating and saving sequences of images
    input_dir = 'C:\\Users\\sukru\\OneDrive - Indiana University\\Projects\\IU\\eyeball-software\\New folder\\' # train1_x.png
    TOTAL_SAMPLES = 1
    input_img = input_dir + 'old SUV.jpg'
    # creating instance - 
    retina = ArtificialRetina(
        #image=input_img,
        P=P,
        foveation_type='static',
        dynamic_foveation_grid_size=(2,2),
        fovea_center=center,
        fovea_radius=15,
        peripheral_active_cones=0,
        fovea_active_rods=0,
        peripheral_gaussianBlur=False,
        peripheral_gaussianBlur_kernal=(21,21),
        peripheral_gaussianBlur_sigma=2,
        peripheral_grayscale=True,
        retinal_warp=True,
        verbose=False,
        display_output=False,
        video=None,
        save_output=False,
        output_dir=None,
    )
    retina_image = retina.apply(input_img)
    # Save the image to the drive
    plt.imshow(retina_image)
    plt.show()