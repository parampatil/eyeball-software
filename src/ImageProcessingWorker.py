import datetime
from PyQt6.QtCore import QDir, QThread, pyqtSignal
from concurrent.futures import ProcessPoolExecutor, as_completed
from ArtificialRetina import ArtificialRetina

def process_image(resolution, fovea_center, fovea_radius, peripheral_active_cones, fovea_active_rods,
                  peripheral_gaussianBlur, peripheral_gaussianBlur_kernal, peripheral_gaussianBlur_sigma,
                  peripheral_grayscale, fovea_type, fovea_grid_size, retinal_warp, verbose, folderPath, fileName, i):

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
    image_path = QDir(folderPath).filePath(fileName)
    processed_image = retina.apply(image_path=image_path)

    return i, processed_image

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
            with ProcessPoolExecutor(self.numCores) as executor:
                futures = [executor.submit(process_image, *self.userInput, self.folderPath, fileName, i)
                            for i, fileName in enumerate(self.imageFiles)]
                for i, future in enumerate(as_completed(futures)):
                    n, processed_image = future.result()
                    self.processedImages[n] = processed_image
                    self.progress.emit(i+1)
                    # Calculate estimated time
                    elapsed_time = datetime.datetime.now() - start_time
                    estimated_time = elapsed_time / (i+1) * (imageFiles_cnt - (i+1))
                    self.estimated_time.emit(f"Estimated Time Remaining: {estimated_time}")
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