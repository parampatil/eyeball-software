import sys
import json
import datetime
import os
import multiprocessing
import mmap

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QHBoxLayout, \
    QRadioButton, QSlider, QCheckBox, QGroupBox, QComboBox, QTabWidget, QButtonGroup, QLineEdit, QProgressBar, QScrollArea, QToolTip, QMessageBox
from PyQt6.QtGui import QIntValidator, QDoubleValidator, QFont, QIcon
from PyQt6.QtCore import QDir, Qt
from PIL import Image
from custom_components import QImagePreview
import numpy as np
from qt_material import apply_stylesheet
from ImageProcessingWorker import ImageProcessingWorker
import validations


class EyeballProject(QMainWindow):
    """EyeballProject's main window (GUI or view)."""

    def __init__(self):
        super().__init__()
        self.folderPath = ""
        self.images = []
        self.imageCount = None
        self.currentThumbnailPage = 0
        self.processedImages = None
        self.processTime = None
        self.retina = None

        QToolTip.setFont(QFont('SansSerif', 10))

        self.init_UI()
        self.showMaximized()

        # if os.path.exists('temp.mmap'):
        #     os.remove('temp.mmap')

    def init_UI(self):
        """Initialises UI elements."""
        self.setWindowTitle("Eyeball Project")
        self.setWindowIcon(QIcon('logo.png'))
        # Main layout and widget
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # region TopLayout
        # Top Layout - houses the folder selector
        self.topGroup = QGroupBox("Load Dataset")
        topLayout = QHBoxLayout()

        # Button to load images
        self.btnLoad = QPushButton('Load Images')
        self.btnLoad.setToolTip(
            "Select a folder containing images to process.")
        self.btnLoad.clicked.connect(self.selectDataset)
        topLayout.addWidget(self.btnLoad, 1)

        # Label to display number of images
        self.imageCountLabel = QLabel('No images selected')
        topLayout.addWidget(self.imageCountLabel, 2)

        # Button to run model
        self.btnRunModel = QPushButton('Run Model')
        self.btnRunModel.setToolTip("Run the model on the selected images.")
        self.btnRunModel.clicked.connect(self.runModel)
        self.btnRunModel.setEnabled(False)
        topLayout.addWidget(self.btnRunModel, 1)

        # Adding top layout to main layout
        self.topGroup.setLayout(topLayout)
        layout.addWidget(self.topGroup)
        # endregion TopLayout

        # region MiddleLayout
        # Middle Layout - houses the image viewer and processing parameters
        midLayout = QHBoxLayout()

        imgViewerLayout = QVBoxLayout()
        imgViewerGroup = QGroupBox("Image Preview")

        # region Tabs
        self.tabWidget = QTabWidget()
        imgViewerLayout.addWidget(self.tabWidget)

        # Tab 1: Input Images
        self.inputTab = QImagePreview()
        self.tabWidget.addTab(self.inputTab, "Input Images")

        # Tab 2: Processed Images
        self.outputTab = QImagePreview()
        self.tabWidget.addTab(self.outputTab, "Processed Images")
        self.tabWidget.setTabEnabled(1, False)
        # endregion Tabs

        imgViewerGroup.setLayout(imgViewerLayout)
        midLayout.addWidget(imgViewerGroup, 3)

        # region ModelParameters

        # Create the scroll area for the sidebar
        self.sidebarLayoutWidgetScroll = QScrollArea()

        # Create the widget that will contain the sidebar layout
        self.sidebarLayoutWidget = QWidget()

        # Create the sidebar layout (QVBoxLayout) and set it to the sidebar widget
        self.sidebarLayout = QVBoxLayout(self.sidebarLayoutWidget)
        self.sidebarLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sidebarLayout.setSpacing(10)

        # Set the sidebar widget to the scroll area
        self.sidebarLayoutWidgetScroll.setWidget(self.sidebarLayoutWidget)
        self.sidebarLayoutWidgetScroll.setWidgetResizable(True)

        # Create a group box for the sidebar and set the scroll area as its widget
        sidebarGroup = QGroupBox("Model Parameters")
        sidebarGroupLayout = QVBoxLayout(sidebarGroup)
        sidebarGroupLayout.addWidget(self.sidebarLayoutWidgetScroll)

        # Add the group box to your main layout (midLayout)
        midLayout.addWidget(sidebarGroup, 1)

        # Inputs in ModelParameters Sidebar
        # Load and Save buttons
        self.LoadSaveLayout = QHBoxLayout()
        # Create load button
        self.load_button = QPushButton("Load Config")
        self.load_button.clicked.connect(self.load_config)
        self.LoadSaveLayout.addWidget(self.load_button)

        # Create save button
        self.save_button = QPushButton("Save Config")
        self.save_button.clicked.connect(self.save_config)
        self.LoadSaveLayout.addWidget(self.save_button)

        self.sidebarLayout.addLayout(self.LoadSaveLayout)

        # Input Resolution
        self.inputResolutionLabel = QLabel("Input Image Resolution (px)")
        self.inputResolutionLabel.setToolTip(
            "Description:Set the resolution of the input images.\nDefault: 224\nMax: 10000")
        self.inputResolutionField = QLineEdit()
        self.inputResolutionField.setPlaceholderText(
            "Enter resolution in format: 224")
        self.intValidator_inputResolutionField = QIntValidator(0, 10000)
        self.inputResolutionField.setValidator(self.intValidator_inputResolutionField)
        self.sidebarLayout.addWidget(self.inputResolutionLabel)
        self.sidebarLayout.addWidget(self.inputResolutionField)

        # Fovea Location X, Y
        self.foveaLocationLabel = QLabel("Fovea Location (x, y)")
        self.foveaLocationLabel.setToolTip(
            "Description: Set the x and y coordinates of the fovea.\nDefault: 112\nMax: 10000")
        foveaLocationLayout = QHBoxLayout()
        self.foveaXField = QLineEdit()
        self.foveaXField.setPlaceholderText("Enter x coordinate")
        self.intValidator_foveaXField = QIntValidator(0, 10000)
        self.foveaXField.setValidator(self.intValidator_foveaXField)
        self.foveaYField = QLineEdit()
        self.foveaYField.setPlaceholderText("Enter y coordinate")
        self.intValidator_foveaYField = QIntValidator(0, 10000)
        self.foveaYField.setValidator(self.intValidator_foveaYField)
        foveaLocationLayout.addWidget(QLabel("x:"))
        foveaLocationLayout.addWidget(self.foveaXField)
        foveaLocationLayout.addWidget(QLabel("y:"))
        foveaLocationLayout.addWidget(self.foveaYField)
        self.sidebarLayout.addWidget(self.foveaLocationLabel)
        self.sidebarLayout.addLayout(foveaLocationLayout)

        # Fovea Radius
        self.foveaRadiusLabel = QLabel("Fovea Radius")
        self.foveaRadiusLabel.setToolTip(
            "Description: Set the radius of the fovea.\nDefault: 1\nMax: 100")
        self.foveaRadiusSlider = QSlider(Qt.Orientation.Horizontal)
        self.foveaRadiusSlider.setRange(1, 100)  # Default range
        self.foveaRadiusSlider.setEnabled(False)  # Disable initially
        self.foveaRadiusValueLabel = QLabel("1")  # Display slider value

        # Layout for Fovea Radius slider and value label
        foveaRadiusLayout = QHBoxLayout()
        foveaRadiusLayout.addWidget(self.foveaRadiusSlider)
        foveaRadiusLayout.addWidget(self.foveaRadiusValueLabel)
        self.sidebarLayout.addWidget(self.foveaRadiusLabel)
        self.sidebarLayout.addLayout(foveaRadiusLayout)

        # Connect Fovea Radius signals to slots
        self.inputResolutionField.textChanged.connect(self.onResolutionChanged)
        self.foveaRadiusSlider.valueChanged.connect(self.onFoveaRadiusChanged)

        # Peripheral Active Cone Cells
        self.peripheralConeCellsLabel = QLabel("Peripheral Active Cone Cells")
        self.peripheralConeCellsLabel.setToolTip(
            "Description: Set the percentage of active cone cells in the peripheral region.\nDefault: 0%\nMax: 100%")
        self.peripheralConeCellsSlider = QSlider(Qt.Orientation.Horizontal)
        self.peripheralConeCellsSlider.setRange(0, 100)

        self.peripheralConeCellsValueLabel = QLabel(
            "0%")  # Display slider value

        # Layout for Peripheral Active Cone Cells slider and value label
        peripheralConeCellsLayout = QHBoxLayout()
        peripheralConeCellsLayout.addWidget(self.peripheralConeCellsSlider)
        peripheralConeCellsLayout.addWidget(self.peripheralConeCellsValueLabel)

        self.sidebarLayout.addWidget(self.peripheralConeCellsLabel)
        self.sidebarLayout.addLayout(peripheralConeCellsLayout)

        # Fovea Active Rod Cells
        self.foveaRodCellsLabel = QLabel("Fovea Active Rod Cells")
        self.foveaRodCellsLabel.setToolTip(
            "Description: Set the percentage of active rod cells in the fovea region.\nDefault: 0%\nMax: 100%")
        self.foveaRodCellsSlider = QSlider(Qt.Orientation.Horizontal)
        self.foveaRodCellsSlider.setRange(0, 100)

        self.foveaRodCellsValueLabel = QLabel("0%")  # Display slider value

        # Layout for Fovea Active Rod Cells slider and value label
        foveaRodCellsLayout = QHBoxLayout()
        foveaRodCellsLayout.addWidget(self.foveaRodCellsSlider)
        foveaRodCellsLayout.addWidget(self.foveaRodCellsValueLabel)

        self.sidebarLayout.addWidget(self.foveaRodCellsLabel)
        self.sidebarLayout.addLayout(foveaRodCellsLayout)

        # Connect signals to slots for updating the value labels
        self.peripheralConeCellsSlider.valueChanged.connect(
            self.onPeripheralConeCellsChanged)
        self.foveaRodCellsSlider.valueChanged.connect(
            self.onFoveaRodCellsChanged)

        # Peripheral Gaussian Blur
        self.peripheralBlurToggle = QCheckBox("Peripheral Gaussian Blur")
        self.peripheralBlurToggle.setToolTip(
            "Description: Enable Gaussian blur in the peripheral region.")
        self.peripheralBlurToggle.stateChanged.connect(
            self.onPeripheralBlurToggled)
        self.sidebarLayout.addWidget(self.peripheralBlurToggle)

        # Peripheral Gaussian Blur Kernal
        self.peripheralBlurKernalLabel = QLabel(
            "Peripheral Gaussian Blur Kernal")
        self.peripheralBlurKernalLabel.setToolTip(
            "Description: Set the kernal size for the Gaussian blur in the peripheral region.\nDefault: (3,3)")
        self.peripheralBlurKernalComboBox = QComboBox()
        self.peripheralBlurKernalComboBox.addItems(
            ["(3,3)", "(5,5)", "(7,7)", "(9,9)", "(11,11)", "(21,21)"])
        self.peripheralBlurKernalComboBox.setItemData(0, (3, 3))
        self.peripheralBlurKernalComboBox.setItemData(1, (5, 5))
        self.peripheralBlurKernalComboBox.setItemData(2, (7, 7))
        self.peripheralBlurKernalComboBox.setItemData(3, (9, 9))
        self.peripheralBlurKernalComboBox.setItemData(4, (11, 11))
        self.peripheralBlurKernalComboBox.setItemData(5, (21, 21))
        self.peripheralBlurKernalLabel.setEnabled(False)
        self.peripheralBlurKernalComboBox.setEnabled(False)
        self.sidebarLayout.addWidget(self.peripheralBlurKernalLabel)
        self.sidebarLayout.addWidget(self.peripheralBlurKernalComboBox)

        # Peripheral Gaussian Sigma
        self.peripheralSigmaLabel = QLabel("Peripheral Gaussian Sigma")
        self.peripheralSigmaLabel.setToolTip(
            "Description: Set the sigma value for the Gaussian blur in the peripheral region.\nDefault: 0.0\nMax: 100.0")
        self.peripheralSigmaField = QLineEdit()
        self.peripheralSigmaLabel.setEnabled(False)
        self.peripheralSigmaField.setEnabled(False)

        # Set a validator to allow only float values in the Gaussian Sigma field
        self.floatValidator = QDoubleValidator(0.0, 100.0, 2)
        self.floatValidator.setNotation(
            QDoubleValidator.Notation.StandardNotation)
        self.peripheralSigmaField.setValidator(self.floatValidator)
        self.peripheralSigmaField.setPlaceholderText("000.00")

        self.sidebarLayout.addWidget(self.peripheralSigmaLabel)
        self.sidebarLayout.addWidget(self.peripheralSigmaField)

        # Peripheral Grayscale
        self.peripheralGrayscaleToggle = QCheckBox("Peripheral Grayscale")
        self.peripheralGrayscaleToggle.setToolTip(
            "Description: Convert the peripheral region to grayscale.")
        self.sidebarLayout.addWidget(self.peripheralGrayscaleToggle)

        # Retinal Warp
        self.retinalWarpToggle = QCheckBox("Retinal Warp")
        self.retinalWarpToggle.setToolTip(
            "Description: Apply retinal warp to the processed images.")
        self.sidebarLayout.addWidget(self.retinalWarpToggle)

        # Fovea Type
        self.foveaTypeLabel = QLabel("Fovea Type")
        self.foveaTypeLabel.setToolTip(
            "Description: Select the type of fovea to simulate.")
        self.foveaTypeStaticRadioButton = QRadioButton("Static")
        self.foveaTypeDynamicRadioButton = QRadioButton("Dynamic")
        self.foveaTypeStaticRadioButton.setChecked(True)  # Default to Static
        self.foveaTypeDynamicRadioButton.toggled.connect(self.onFoveaTypeSelected)

        # Group the Fovea Type radio buttons
        self.foveaTypeGroup = QButtonGroup(self)
        self.foveaTypeGroup.addButton(self.foveaTypeStaticRadioButton)
        self.foveaTypeGroup.addButton(self.foveaTypeDynamicRadioButton)

        foveaTypeLayout = QHBoxLayout()
        foveaTypeLayout.addWidget(self.foveaTypeStaticRadioButton)
        foveaTypeLayout.addWidget(self.foveaTypeDynamicRadioButton)
        self.sidebarLayout.addWidget(self.foveaTypeLabel)
        self.sidebarLayout.addLayout(foveaTypeLayout)

        self.dynamicFoveaGridSizeLabel = QLabel("Dynamic Fovea Grid Size")
        self.dynamicFoveaGridSizeLabel.setToolTip("Description: Set the grid size for the Dynamic Fovea.")

        self.dynamicFoveaGridSizeField = QLineEdit()
        self.dynamicFoveaGridSizeField.setPlaceholderText("0")
        self.dynamicFoveaIntValidator = QIntValidator(0,100)
        self.dynamicFoveaGridSizeField.setValidator(self.dynamicFoveaIntValidator)
        self.dynamicFoveaGridSizeField.setEnabled(False)
        self.dynamicFoveaGridSizeLabel.setEnabled(False)

        self.sidebarLayout.addWidget(self.dynamicFoveaGridSizeLabel)
        self.sidebarLayout.addWidget(self.dynamicFoveaGridSizeField)

        # Verbose
        self.verboseToggle = QCheckBox("Verbose")
        self.verboseToggle.setToolTip(
            "Description: Save the log of the model run.")
        self.sidebarLayout.addWidget(self.verboseToggle)

        # Multiprocessing Toggle
        self.multiprocessingToggle = QCheckBox("Multiprocessing")
        self.multiprocessingToggle.setToolTip(
            "Description: Enable multiprocessing for faster processing.\nDefault: Disabled")
        self.sidebarLayout.addWidget(self.multiprocessingToggle)
        self.multiprocessingToggle.stateChanged.connect(
            self.onMultiprocessingToggled)

        # Number of cores
        num_cores = os.cpu_count()
        self.numCoresLabel = QLabel("Number of Cores")
        self.numCoresLabel.setToolTip(f"Description: Set the number of cores to use for multiprocessing.\nDefault: {
                                      num_cores-1} \nMax: {num_cores}")
        self.numCoresComboBox = QComboBox()
        self.numCoresComboBox.addItems([str(i) for i in range(1, num_cores+1)])
        for i in range(1, num_cores+1):
            self.numCoresComboBox.setItemData(i-1, i)
        self.numCoresComboBox.setCurrentText(str(num_cores-1))
        self.sidebarLayout.addWidget(self.numCoresLabel)
        self.sidebarLayout.addWidget(self.numCoresComboBox)
        self.numCoresLabel.setEnabled(False)
        self.numCoresComboBox.setEnabled(False)

        # Eye Type
        self.eyeTypeLabel = QLabel("Eye Type")
        self.eyeTypeLabel.setToolTip(
            "Description: Select the type of eye to simulate.")
        self.eyeTypeSingleRadioButton = QRadioButton("Single Eye")
        self.eyeTypeDualRadioButton = QRadioButton("Dual Eye")
        self.eyeTypeSingleRadioButton.setChecked(True)  # Default to Single Eye

        # Group the Eye Type radio buttons
        self.eyeTypeGroup = QButtonGroup(self)
        self.eyeTypeGroup.addButton(self.eyeTypeSingleRadioButton)
        self.eyeTypeGroup.addButton(self.eyeTypeDualRadioButton)

        eyeTypeLayout = QHBoxLayout()
        eyeTypeLayout.addWidget(self.eyeTypeSingleRadioButton)
        eyeTypeLayout.addWidget(self.eyeTypeDualRadioButton)
        self.sidebarLayout.addWidget(self.eyeTypeLabel)
        self.sidebarLayout.addLayout(eyeTypeLayout)

        # Adding middle layout to main layout
        layout.addLayout(midLayout)
        # endregion MiddleLayout

        # region BottomLayout
        # BottomLayer - Save options and progress bar
        self.bottomGroup = QGroupBox("Save Options")
        bottomLayout = QHBoxLayout()

        # Button to save images
        self.btnSave = QPushButton('Save Images')
        self.btnSave.setToolTip("Save the processed images to a directory.")
        self.btnSave.clicked.connect(self.saveImages)
        self.btnSave.setEnabled(False)
        bottomLayout.addWidget(self.btnSave, 1)

        # Label to display save directory
        self.saveDirLabel = QLabel('No directory selected')
        bottomLayout.addWidget(self.saveDirLabel, 2)

        # Progress Layout
        self.progressLayout = QVBoxLayout()
        self.progressLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        bottomLayout.addLayout(self.progressLayout, 1)

        # Progress Bar
        self.progressBar = QProgressBar()
        self.progressBar.minimum = 0
        self.progressBar.setVisible(False)
        self.progressLayout.addWidget(self.progressBar)
        # bottomLayout.addWidget(self.progressBar, 1)
        self.progressBar.setStyleSheet("color: black")

        # Estimated Time Remaining
        self.estimatedTimeLabel = QLabel("")
        self.progressLayout.addWidget(self.estimatedTimeLabel)
        # bottomLayout.addWidget(self.estimatedTimeLabel, 1)

        self.bottomGroup.setLayout(bottomLayout)
        layout.addWidget(self.bottomGroup)
        # endregion BottomLayout

    def selectDataset(self):
        folderPath = QFileDialog.getExistingDirectory(
            self, 'Select Folder Containing Images')
        if folderPath:
            dir = QDir(folderPath)
            dir.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.bmp"])
            self.imageFiles = dir.entryList()
            self.imageCount = len(self.imageFiles)
        
            if self.imageCount == 0:
                self.alert(f'No Images Found in {folderPath}', "Warning")
                self.btnRunModel.setEnabled(False)
                self.imageCountLabel.setText("No images found")
                return
        
            self.imageCountLabel.setWordWrap(True)
            self.imageCountLabel.setText(
                f'Path: {folderPath}, Images found: {self.imageCount}')
            self.alert(f'Path: {folderPath}, Images found: {
                       self.imageCount}', "Information")
        
            self.folderPath = folderPath
            self.inputTab.setImagePath(
                folder=folderPath, images=self.imageFiles)
            self.btnRunModel.setEnabled(True)
            self.btnRunModel.setStyleSheet("background-color: green")
            self.tabWidget.setCurrentIndex(0)
            self.progressBar.setMaximum(self.imageCount)
            self.progressBar.setValue(0)

    def colletUserInput(self):
        # TODO: this needs a standardized representation - class model.
        # Validate & gather the input parameters
        resolution = self.inputResolutionField.text()
        if validations.isInt(resolution, "Resolution"):
            resolution = int(resolution)

        fov_x, fov_y = self.foveaXField.text(), self.foveaYField.text()
        if validations.isInt(fov_x, "Fovea X") and validations.isInt(fov_y, "Fovea Y"):
            fov_x, fov_y = int(self.foveaXField.text()), int(
                self.foveaYField.text())
        fovea_center = (fov_x, fov_y)

        fovea_radius = self.foveaRadiusSlider.value()

        peripheral_active_cones = self.peripheralConeCellsSlider.value()

        fovea_active_rods = self.foveaRodCellsSlider.value()

        peripheral_gaussianBlur = self.peripheralBlurToggle.isChecked()

        if peripheral_gaussianBlur:
            peripheral_gaussianBlur_kernal = self.peripheralBlurKernalComboBox.currentData()
            peripheral_gaussianBlur_sigma = float(self.peripheralSigmaField.text()) if validations.isFloat(self.peripheralSigmaField.text(), "Peripheral Sigma") else 0
        else:
            peripheral_gaussianBlur_kernal, peripheral_gaussianBlur_sigma = None, None

        peripheral_grayscale = self.peripheralGrayscaleToggle.isChecked()

        fovea_type = "dynamic" if self.foveaTypeDynamicRadioButton.isChecked() else "static"

        fovea_grid_size = int(self.dynamicFoveaGridSizeField.text()) if self.foveaTypeDynamicRadioButton.isChecked() and validations.isInt(self.dynamicFoveaGridSizeField.text(), "Dynamic Fovea Grid Size") else 0
        fovea_grid_size = (fovea_grid_size, fovea_grid_size)

        retinal_warp = self.retinalWarpToggle.isChecked()

        verbose = self.verboseToggle.isChecked()

        return resolution, fovea_center, fovea_radius, peripheral_active_cones, fovea_active_rods, peripheral_gaussianBlur, peripheral_gaussianBlur_kernal, peripheral_gaussianBlur_sigma, peripheral_grayscale, \
           fovea_type, fovea_grid_size, retinal_warp, verbose

    def save_log(self, userInput):
        filename = f"Log {datetime.datetime.now().strftime(
            '%Y-%m-%d_%H-%M-%S')}.txt"

        info = f'''
        Image Information:
        -----------------
        Image size: {userInput[0]}x{userInput[0]}

        Fovea Information:
        ------------------
        Fovea type: {userInput[9]}
        Dynamic fovea grid size: {userInput[10]}
        Fovea center: {userInput[1]}
        Fovea radius: {userInput[2]}
        Peripheral active rods: {userInput[4]}%

        Peripheral Information:
        -----------------------
        Peripheral active cones: {userInput[3]}%
        Peripheral Gaussian Blur: {userInput[5]}
        Peripheral Gaussian Blur Kernal: {userInput[6]}
        Peripheral Gaussian Blur Sigma: {userInput[7]}
        Peripheral Grayscale: {userInput[8]}

        Additional Settings:
        --------------------
        Retinal Warp: {userInput[11]}

        Run Information:
        ----------------
        Number of images: {self.imageCount}
        Multiprocessing: {self.multiprocessingToggle.isChecked()}
        Number of cores: {self.numCoresComboBox.currentData()}
        Processing Time: {self.processTime}
        '''

        self.processTime = None

        with open(filename, "w") as file:
            file.write(info)

    def runModel(self):
        self.loadingStateEnable()
        try:
            userInput = [*self.colletUserInput()]

            # Initialize the memmap object to store the processed images
            if self.processedImages is None or len(self.processedImages) == 0:
                self.processedImages = self.create_memmap(
                    # Running the model for the first time
                    (len(self.imageFiles), userInput[0], userInput[0], 3))
            else:
                # Rerun the model with new parameters
                self.refresh_memmap(
                    (len(self.imageFiles), userInput[0], userInput[0], 3))

            # Report the estimated time
            def estimate_time(est_time):
                self.estimatedTimeLabel.setText(est_time)

            def setProcessTime(time):
                self.processTime = time
                
            def processing_finished(processedImages):
                # Save the log if verbose is enabled
                if self.verboseToggle.isChecked():
                    self.save_log(userInput)

                self.loadingStateDisable()
                self.outputTab.setImages(images=processedImages)
                self.tabWidget.setTabEnabled(1, True)
                self.tabWidget.setCurrentIndex(1)
                self.btnSave.setEnabled(True)
                self.alert("Model run successfully.", "Information")
                self.btnSave.setStyleSheet("background-color: green")
                del processedImages
                print("Processing finished")
                del self.worker

            # Create a worker thread to process the images
            self.worker = ImageProcessingWorker(userInput, self.folderPath, self.imageFiles, self.multiprocessingToggle.isChecked(
            ), self.numCoresComboBox.currentData(), self.processedImages)
            self.worker.progress.connect(self.progressBar.setValue)
            self.worker.result.connect(processing_finished)
            self.worker.estimated_time.connect(estimate_time)
            self.worker.processTime.connect(setProcessTime)
            self.worker.start()

        except validations.ValidationException as e:
            self.loadingStateDisable()
            self.alert(f"Validation Failed: {str(e)}", "Error")
            print(f"Validation Failed: {str(e)}")
        except Exception as e:
            self.loadingStateDisable()
            self.alert(f"An error occurred: {str(e)}", "Error")
            print(f"An error occurred: {str(e)}")

    def saveImages(self):
        saveDir = QFileDialog.getExistingDirectory(
            self, 'Select Directory to Save Images')
        if saveDir:
            self.saveDirLabel.setText(f'Save directory: {saveDir}')
            for i, image in enumerate(self.processedImages):
                Image.fromarray(image).save(
                    QDir(saveDir).filePath(self.imageFiles[i]))
            self.alert(f"Saved {len(self.processedImages)} images to {saveDir}", "Information")
            print(f'Saved {len(self.processedImages)} images to {saveDir}')

    def create_memmap(self, size, path='temp.mmap', dtype='uint8', mode='w+'):
        """Creates a np memmap object to store and access large np arrays dynamically from disk. 
        Use this to hold the processed output images."""
        return np.memmap(filename=path, dtype=dtype, mode=mode, shape=size)

    def refresh_memmap(self, shape):
        self.outputTab.clearThumbnails()
        self.outputTab.clearImagePreview()
        self.outputTab.images = None
        # premature optimization
        if self.imageCount != len(self.processedImages) or shape[1] != self.processedImages.shape[1]:
            self.destroy_memmap()
            self.processedImages = self.create_memmap(shape)
        return

    def destroy_memmap(self):
        self.processedImages = None
        self.outputTab.images = None
        os.remove('temp.mmap')

    def load_config(self):
        print("Loading config data...")
        filePath = QFileDialog.getOpenFileName(
            self, 'Open Config File', '', 'JSON Files (*.json)')[0]
        if filePath:
            try:
                with open(filePath, 'r') as file:
                    data = json.load(file)
                    self.inputResolutionField.setText(
                        str(data['input_resolution']))
                    self.foveaXField.setText(str(data['fovea_x']))
                    self.foveaYField.setText(str(data['fovea_y']))
                    self.foveaRadiusSlider.setValue(data['fovea_radius'])
                    self.peripheralConeCellsSlider.setValue(
                        data['peripheral_active_cones'])
                    self.foveaRodCellsSlider.setValue(
                        data['fovea_active_rods'])
                    self.peripheralBlurToggle.setChecked(
                        data['peripheral_gaussianBlur'])
                    self.peripheralBlurKernalComboBox.setCurrentText(
                        data['peripheral_gaussianBlur_kernal'])
                    self.peripheralSigmaField.setText(
                        str(data['peripheral_gaussianBlur_sigma']))
                    self.peripheralGrayscaleToggle.setChecked(
                        data['peripheral_grayscale'])
                    self.retinalWarpToggle.setChecked(data['retinal_warp'])
                    self.verboseToggle.setChecked(data['verbose'])
                    self.eyeTypeSingleRadioButton.setChecked(
                        data['eye_type'] == "Single Eye")
                    self.eyeTypeDualRadioButton.setChecked(
                        data['eye_type'] == "Dual Eye")
                    self.foveaTypeStaticRadioButton.setChecked(
                        data['fovea_type'] == "Static")
                    self.foveaTypeDynamicRadioButton.setChecked(
                        data['fovea_type'] == "Dynamic")
                    if self.foveaTypeDynamicRadioButton.isChecked():
                        self.dynamicFoveaGridSizeField.setText(data['fovea_grid_size'])

                    print("Config Data loaded.")
            except Exception as e:
                self.alert(f"An error occurred: {str(e)}", "Error")
                print(f"An error occurred: {str(e)}")
        else:
            self.alert("No file path selected.", "Error")
            print("No file path selected.")

    def save_config(self):
        print("Saving data...")
        filePath = QFileDialog.getSaveFileName(
            self, 'Save Config File', '', 'JSON Files (*.json)')[0]
        if filePath:
            try:
                data = {
                    'input_resolution': int(self.inputResolutionField.text()),
                    'fovea_x': int(self.foveaXField.text()),
                    'fovea_y': int(self.foveaYField.text()),
                    'fovea_radius': self.foveaRadiusSlider.value(),
                    'peripheral_active_cones': self.peripheralConeCellsSlider.value(),
                    'fovea_active_rods': self.foveaRodCellsSlider.value(),
                    'peripheral_gaussianBlur': self.peripheralBlurToggle.isChecked(),
                    'peripheral_gaussianBlur_kernal': self.peripheralBlurKernalComboBox.currentText(),
                    'peripheral_gaussianBlur_sigma': float(self.peripheralSigmaField.text()),
                    'peripheral_grayscale': self.peripheralGrayscaleToggle.isChecked(),
                    'retinal_warp': self.retinalWarpToggle.isChecked(),
                    'verbose': self.verboseToggle.isChecked(),
                    'eye_type': "Single Eye" if self.eyeTypeSingleRadioButton.isChecked() else "Dual Eye",
                    'fovea_type': "Static" if self.foveaTypeStaticRadioButton.isChecked() else "Dynamic",
                    'fovea_grid_size': self.dynamicFoveaGridSizeField.text()
                }
                with open(filePath, 'w') as file:
                    json.dump(data, file, indent=4)
                self.alert(f"Config saved at {filePath}", "Information")
            except Exception as e:
                self.alert(f"An error occurred: {str(e)}", "Error")
                print(f"An error occurred: {str(e)}")
            print("Data saved.")
        else:
            self.alert("No file path selected.", "Error")
            print("No file path selected.")

    # Sidebar Event Handlers
    # Define the slot to enable the slider and set its maximum value
    def onResolutionChanged(self):
        resolution_text = self.inputResolutionField.text()
        if resolution_text.isdigit():
            resolution = int(resolution_text)
            self.foveaRadiusSlider.setMaximum(resolution)
            self.foveaRadiusSlider.setEnabled(True)
        else:
            # Disable if input is not valid
            self.foveaRadiusSlider.setEnabled(False)

    # Define the slot to update the slider value label
    def onFoveaRadiusChanged(self, value):
        self.foveaRadiusValueLabel.setText(str(value))

    # Define the slot to update the Peripheral Active Cone Cells value label
    def onPeripheralConeCellsChanged(self, value):
        self.peripheralConeCellsValueLabel.setText(f"{value}%")

    # Define the slot to update the Fovea Active Rod Cells value label
    def onFoveaRodCellsChanged(self, value):
        self.foveaRodCellsValueLabel.setText(f"{value}%")

    # Slot to handle the state change of the Peripheral Gaussian Blur toggle
    def onPeripheralBlurToggled(self, state):
        is_enabled = True if state == 2 else False
        self.peripheralBlurKernalLabel.setEnabled(is_enabled)
        self.peripheralBlurKernalComboBox.setEnabled(is_enabled)
        self.peripheralSigmaLabel.setEnabled(is_enabled)
        self.peripheralSigmaField.setEnabled(is_enabled)

    # Slot to handle the state change of the Multiprocessing toggle
    def onMultiprocessingToggled(self, state):
        is_enabled = True if state == 2 else False
        self.numCoresLabel.setEnabled(is_enabled)
        self.numCoresComboBox.setEnabled(is_enabled)

    def onFoveaTypeSelected(self, selected):
        self.dynamicFoveaGridSizeLabel.setEnabled(selected)
        self.dynamicFoveaGridSizeField.setEnabled(selected)

    # Loading State - Disable all buttons
    def loadingStateEnable(self):
        self.btnSave.setEnabled(False)
        self.progressBar.reset()
        self.progressBar.setVisible(True)
        self.sidebarLayoutWidget.setEnabled(False)

    # Loading State - Enable all buttons
    def loadingStateDisable(self):
        self.sidebarLayoutWidget.setEnabled(True)

    # Aletr Message Box
    def alert(self, message: str, title: str = "Information"):
        msg = QMessageBox()
        if title == "Error":
            msg.setIcon(QMessageBox.Icon.Critical)
        elif title == "Warning":
            msg.setIcon(QMessageBox.Icon.Warning)
        else:
            msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setMinimumWidth(200)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    # Clean up the temp file before closing the window
    def closeEvent(self, event):
        try:
            self.destroy_memmap()

            if os.path.exists('temp.mmap'):
                os.remove('temp.mmap')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            self.alert(f"An error occurred: {str(e)}", "Error")

def main():
    """EyeballProject's main function."""
    pyApp = QApplication([])
    extra = {
        'density_scale': '-1'
    }
    apply_stylesheet(pyApp, theme='dark_teal.xml', extra=extra)
    pyApp.setStyleSheet(
        pyApp.styleSheet() + ("QLineEdit { color: white } QComboBox { color: white }"))
    pyAppWindow = EyeballProject()
    pyAppWindow.show()
    sys.exit(pyApp.exec())

if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method('spawn', force=True)
    main()