import datetime, os, multiprocessing
from PyQt6.QtCore import QDir, QThread, pyqtSignal
from concurrent.futures import ProcessPoolExecutor, as_completed
from ArtificialRetina import ArtificialRetina
import traceback

def process_image(resolution, fovea_center, fovea_radius, peripheral_active_cones, fovea_active_rods,
                  peripheral_gaussianBlur, peripheral_gaussianBlur_kernal, peripheral_gaussianBlur_sigma,
                  peripheral_grayscale, fovea_type, fovea_grid_size, retinal_warp, verbose, folderPath, fileName, i):
    try:
        # Create the retina object within the worker process
        retina = ArtificialRetina(
            P=resolution,
            fovea_center=fovea_center,
            fovea_radius=fovea_radius,
            peripheral_active_cones=peripheral_active_cones,
            fovea_active_rods=fovea_active_rods,
            peripheral_gaussianBlur=peripheral_gaussianBlur,
            peripheral_gaussianBlur_kernal=peripheral_gaussianBlur_kernal,
            peripheral_gaussianBlur_sigma=peripheral_gaussianBlur_sigma,
            peripheral_grayscale=peripheral_grayscale,
            foveation_type = fovea_type,
            dynamic_foveation_grid_size=fovea_grid_size,
            retinal_warp=retinal_warp,
            verbose=verbose
        )

        # Process the image
        image_path = os.path.join(folderPath, fileName)
        processed_image = retina.apply(image_path=image_path)
        return i, processed_image
    except Exception as e:
        print(f"Error processing image {fileName}: {str(e)}")
        return i, None


class ImageProcessingWorker(QThread):
    progress = pyqtSignal(int)
    estimated_time = pyqtSignal(object)
    result = pyqtSignal(object)
    processTime = pyqtSignal(object)

    def __init__(self, userInput, folderPath, imageFiles, multiprocessingToggle, numCores, processedImages):
        super().__init__()
        self.userInput = userInput
        self.folderPath = folderPath
        self.imageFiles = imageFiles
        self.multiprocessingToggle = multiprocessingToggle
        self.processedImages = processedImages
        self.numCores = numCores

    def __del__(self):
        print("Thread exited")

    def run(self):
        start_time = datetime.datetime.now()
        imageFiles_cnt = len(self.imageFiles)
        if self.multiprocessingToggle:
           with multiprocessing.Pool(processes=self.numCores) as pool:
                results = []
                for i, fileName in enumerate(self.imageFiles):
                    result = pool.apply_async(process_image, (*self.userInput, self.folderPath, fileName, i))
                    results.append(result)

                for i, result in enumerate(results):
                    try:
                        n, processed_image = result.get()
                        if processed_image is not None:
                            self.processedImages[n] = processed_image
                        self.progress.emit(i+1)
                        
                        # Calculate estimated time
                        elapsed_time = datetime.datetime.now() - start_time
                        estimated_time = elapsed_time / (i+1) * (imageFiles_cnt - (i+1))
                        self.estimated_time.emit(f"Estimated Time Remaining: {estimated_time}")
                    except Exception as e:
                        print(f"Error processing future: {str(e)}")
        else:
            retina = self.generate_retina_object(*self.userInput)
            for i, fileName in enumerate(self.imageFiles):
                image_path = QDir(self.folderPath).filePath(fileName)
                self.processedImages[i] = retina.apply(image_path=image_path)
                self.progress.emit(i+1)
                # Calculate estimated time
                elapsed_time = datetime.datetime.now() - start_time
                estimated_time = elapsed_time / (i+1) * (imageFiles_cnt - (i+1))
                self.estimated_time.emit(f"Estimated Time Remaining: {estimated_time}")
        
        end_time = datetime.datetime.now()
        print(f"Time taken: {end_time - start_time}")
        self.estimated_time.emit(f"Time taken: {end_time - start_time}")
        self.processTime.emit(f"{end_time - start_time}")
        self.result.emit(self.processedImages)
    
    # Generate the retina object
    def generate_retina_object(self, resolution, fovea_center, fovea_radius, peripheral_active_cones, fovea_active_rods, peripheral_gaussianBlur, peripheral_gaussianBlur_kernal, peripheral_gaussianBlur_sigma, peripheral_grayscale, fovea_type, fovea_grid_size, retinal_warp, verbose):
        retina = ArtificialRetina(P=resolution,
                                    foveation_type = fovea_type,
                                    dynamic_foveation_grid_size=fovea_grid_size,
                                    fovea_center=fovea_center,
                                    fovea_radius=fovea_radius,
                                    peripheral_active_cones=peripheral_active_cones,
                                    fovea_active_rods=fovea_active_rods,
                                    peripheral_gaussianBlur=peripheral_gaussianBlur,
                                    peripheral_gaussianBlur_kernal=peripheral_gaussianBlur_kernal,
                                    peripheral_gaussianBlur_sigma=peripheral_gaussianBlur_sigma,
                                    peripheral_grayscale=peripheral_grayscale,
                                    retinal_warp=retinal_warp,
                                    verbose=verbose)
        return retina