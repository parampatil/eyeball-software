import sys, json, datetime

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QHBoxLayout,\
        QRadioButton, QSlider, QCheckBox, QGroupBox, QComboBox, QTabWidget, QButtonGroup, QLineEdit, QProgressBar, QScrollArea, QToolTip
from PyQt6.QtGui import QIntValidator, QDoubleValidator, QFont, QIcon
from PyQt6.QtCore import QDir, Qt
from PIL import Image
from custom_components import QImagePreview
import numpy as np 
from qt_material import apply_stylesheet
from ArtificialRetina import ArtificialRetina
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

        QToolTip.setFont(QFont('SansSerif', 10))

        self.init_UI()
        self.showMaximized()

        self.retina = None
    
    def init_UI(self):
        """Initialises UI elements."""
        self.setWindowTitle("Eyeball Project")
        self.setWindowIcon(QIcon('logo.png'))
        # Main layout and widget
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        #region TopLayout
        # Top Layout - houses the folder selector
        self.topGroup = QGroupBox("Load Dataset")
        topLayout = QHBoxLayout()

        # Button to load images
        self.btnLoad = QPushButton('Load Images')
        self.btnLoad.setToolTip("Select a folder containing images to process.")
        self.btnLoad.clicked.connect(self.selectDataset)
        topLayout.addWidget(self.btnLoad,1)

        # Label to display number of images
        self.imageCountLabel = QLabel('No images selected')
        topLayout.addWidget(self.imageCountLabel,2)

        # Button to run model
        self.btnRunModel = QPushButton('Run Model')
        self.btnRunModel.setToolTip("Run the model on the selected images.")
        self.btnRunModel.clicked.connect(self.runModel)
        self.btnRunModel.setEnabled(False)
        topLayout.addWidget(self.btnRunModel,1)
        
        # Adding top layout to main layout
        self.topGroup.setLayout(topLayout)
        layout.addWidget(self.topGroup)
        #endregion TopLayout

        #region MiddleLayout
        # Middle Layout - houses the image viewer and processing parameters
        midLayout = QHBoxLayout()

        imgViewerLayout = QVBoxLayout()
        imgViewerGroup = QGroupBox("Image Preview")

        #region Tabs
        self.tabWidget = QTabWidget()
        imgViewerLayout.addWidget(self.tabWidget)

        # Tab 1: Input Images
        self.inputTab = QImagePreview()
        self.tabWidget.addTab(self.inputTab, "Input Images")

        # Tab 2: Processed Images
        self.outputTab = QImagePreview()
        self.tabWidget.addTab(self.outputTab, "Processed Images")
        self.tabWidget.setTabEnabled(1,False)
        #endregion Tabs
        
        imgViewerGroup.setLayout(imgViewerLayout)
        midLayout.addWidget(imgViewerGroup,3)
        
        #region ModelParameters
        
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
        self.inputResolutionLabel.setToolTip("Description:Set the resolution of the input images.\nDefault: 224\nMax: 10000")
        self.inputResolutionField = QLineEdit()
        self.inputResolutionField.setPlaceholderText("Enter resolution in format: 224")
        self.intValidator_inputResolutionField = QIntValidator(0, 10000)
        self.inputResolutionField.setValidator(self.intValidator_inputResolutionField)
        self.sidebarLayout.addWidget(self.inputResolutionLabel)
        self.sidebarLayout.addWidget(self.inputResolutionField)

        # Fovea Location X, Y
        self.foveaLocationLabel = QLabel("Fovea Location (x, y)")
        self.foveaLocationLabel.setToolTip("Description: Set the x and y coordinates of the fovea.\nDefault: 112\nMax: 10000")
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
        self.foveaRadiusLabel.setToolTip("Description: Set the radius of the fovea.\nDefault: 1\nMax: 100")
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
        self.peripheralConeCellsLabel.setToolTip("Description: Set the percentage of active cone cells in the peripheral region.\nDefault: 0%\nMax: 100%")
        self.peripheralConeCellsSlider = QSlider(Qt.Orientation.Horizontal)
        self.peripheralConeCellsSlider.setRange(0, 100)

        self.peripheralConeCellsValueLabel = QLabel("0%")  # Display slider value

        # Layout for Peripheral Active Cone Cells slider and value label
        peripheralConeCellsLayout = QHBoxLayout()
        peripheralConeCellsLayout.addWidget(self.peripheralConeCellsSlider)
        peripheralConeCellsLayout.addWidget(self.peripheralConeCellsValueLabel)

        self.sidebarLayout.addWidget(self.peripheralConeCellsLabel)
        self.sidebarLayout.addLayout(peripheralConeCellsLayout)

        # Fovea Active Rod Cells
        self.foveaRodCellsLabel = QLabel("Fovea Active Rod Cells")
        self.foveaRodCellsLabel.setToolTip("Description: Set the percentage of active rod cells in the fovea region.\nDefault: 0%\nMax: 100%")
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
        self.peripheralConeCellsSlider.valueChanged.connect(self.onPeripheralConeCellsChanged)
        self.foveaRodCellsSlider.valueChanged.connect(self.onFoveaRodCellsChanged)
                
        # Peripheral Gaussian Blur
        self.peripheralBlurToggle = QCheckBox("Peripheral Gaussian Blur")
        self.peripheralBlurToggle.setToolTip("Description: Enable Gaussian blur in the peripheral region.")
        self.peripheralBlurToggle.stateChanged.connect(self.onPeripheralBlurToggled)
        self.sidebarLayout.addWidget(self.peripheralBlurToggle)

        # Peripheral Gaussian Blur Kernal
        self.peripheralBlurKernalLabel = QLabel("Peripheral Gaussian Blur Kernal")
        self.peripheralBlurKernalLabel.setToolTip("Description: Set the kernal size for the Gaussian blur in the peripheral region.\nDefault: (3,3)")
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
        self.peripheralSigmaLabel.setToolTip("Description: Set the sigma value for the Gaussian blur in the peripheral region.\nDefault: 0.0\nMax: 100.0")
        self.peripheralSigmaField = QLineEdit()
        self.peripheralSigmaLabel.setEnabled(False)
        self.peripheralSigmaField.setEnabled(False)

        # Set a validator to allow only float values in the Gaussian Sigma field
        self.floatValidator = QDoubleValidator(0.0, 100.0, 2)
        self.floatValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.peripheralSigmaField.setValidator(self.floatValidator)
        self.peripheralSigmaField.setPlaceholderText("000.00")

        self.sidebarLayout.addWidget(self.peripheralSigmaLabel)
        self.sidebarLayout.addWidget(self.peripheralSigmaField)

        # Peripheral Grayscale
        self.peripheralGrayscaleToggle = QCheckBox("Peripheral Grayscale")
        self.peripheralGrayscaleToggle.setToolTip("Description: Convert the peripheral region to grayscale.")
        self.sidebarLayout.addWidget(self.peripheralGrayscaleToggle)

        # Retinal Warp
        self.retinalWarpToggle = QCheckBox("Retinal Warp")
        self.retinalWarpToggle.setToolTip("Description: Apply retinal warp to the processed images.")
        self.sidebarLayout.addWidget(self.retinalWarpToggle)

        # Verbose
        self.verboseToggle = QCheckBox("Verbose")
        self.verboseToggle.setToolTip("Description: Save the log of the model run.")
        self.sidebarLayout.addWidget(self.verboseToggle)

        # Eye Type
        self.eyeTypeLabel = QLabel("Eye Type")
        self.eyeTypeLabel.setToolTip("Description: Select the type of eye to simulate.")
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

        # Fovea Type
        self.foveaTypeLabel = QLabel("Fovea Type")
        self.foveaTypeLabel.setToolTip("Description: Select the type of fovea to simulate.")
        self.foveaTypeStaticRadioButton = QRadioButton("Static")
        self.foveaTypeDynamicRadioButton = QRadioButton("Dynamic")
        self.foveaTypeStaticRadioButton.setChecked(True)  # Default to Static

        # Group the Fovea Type radio buttons
        self.foveaTypeGroup = QButtonGroup(self)
        self.foveaTypeGroup.addButton(self.foveaTypeStaticRadioButton)
        self.foveaTypeGroup.addButton(self.foveaTypeDynamicRadioButton)

        foveaTypeLayout = QHBoxLayout()
        foveaTypeLayout.addWidget(self.foveaTypeStaticRadioButton)
        foveaTypeLayout.addWidget(self.foveaTypeDynamicRadioButton)
        self.sidebarLayout.addWidget(self.foveaTypeLabel)
        self.sidebarLayout.addLayout(foveaTypeLayout)

        # Adding middle layout to main layout
        layout.addLayout(midLayout)
        #endregion MiddleLayout

        #region BottomLayout
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

        # Progress Bar
        self.progressBar = QProgressBar()
        self.progressBar.minimum = 0
        self.progressBar.setVisible(False)
        bottomLayout.addWidget(self.progressBar, 1)
        self.progressBar.setStyleSheet("color: black")

        self.bottomGroup.setLayout(bottomLayout)
        layout.addWidget(self.bottomGroup)
        #endregion BottomLayout

    def selectDataset(self):
        folderPath = QFileDialog.getExistingDirectory(self, 'Select Folder Containing Images')
        if folderPath:
            dir = QDir(folderPath)
            dir.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.bmp"])
            self.imageFiles = dir.entryList()
            self.imageCount = len(self.imageFiles)

            #TODO: handle exception
            if self.imageCount == 0:
                raise ValueError(f"No Images Found in {folderPath}")

            self.imageCountLabel.setWordWrap(True)
            self.imageCountLabel.setText(f'Path: {folderPath}, Images found: {self.imageCount}')
            validations.alert(f'Path: {folderPath}, Images found: {self.imageCount}', "Information")
            

            self.folderPath = folderPath
            self.inputTab.setImagePath(folder=folderPath, images=self.imageFiles)
            self.btnRunModel.setEnabled(True)
            self.btnRunModel.setStyleSheet("background-color: green")
            self.processedImages = None

            self.progressBar.setMaximum(self.imageCount)
        #self.showMaximized()

    def runModel(self):
        try:
            resolution = self.inputResolutionField.text()
            if validations.isInt(resolution, "Resolution"):
                resolution = int(resolution)

            fov_x, fov_y = self.foveaXField.text() ,self.foveaYField.text()
            if validations.isInt(fov_x, "Fovea X") and validations.isInt(fov_y, "Fovea Y"):
                fov_x, fov_y = int(self.foveaXField.text()) , int(self.foveaYField.text())
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

            retinal_warp = self.retinalWarpToggle.isChecked()

            # Process the images based on the selected parameters
            retina = ArtificialRetina(P = resolution,
                                    fovea_center = fovea_center,
                                    fovea_radius = fovea_radius,
                                    peripheral_active_cones = peripheral_active_cones,
                                    fovea_active_rods = fovea_active_rods,
                                    peripheral_gaussianBlur = peripheral_gaussianBlur,
                                    peripheral_gaussianBlur_kernal = peripheral_gaussianBlur_kernal,
                                    peripheral_gaussianBlur_sigma = peripheral_gaussianBlur_sigma,
                                    peripheral_grayscale = peripheral_grayscale,
                                    retinal_warp = retinal_warp,
                                    verbose=self.verboseToggle.isChecked())
            if self.verboseToggle.isChecked():
                filename = f"Log {datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
                with open(filename, "w") as file:
                    file.write(retina.display_info())
                    
            self.loadingStateEnable()
            if self.processedImages is None or len(self.processedImages) == 0:
                self.processedImages = self.create_memmap((len(self.imageFiles), retina.P, retina.P, 3)) 
            else:
                self.refresh_memmap((len(self.imageFiles), retina.P, retina.P, 3))
            
            for i, fileName in enumerate(self.imageFiles):
                print(f"{i}/{self.imageCount}, {fileName}")
                self.processedImages[i] = retina.apply(image_path=QDir(self.folderPath).filePath(fileName))
                self.progressBar.setValue(i+1)
            
            self.loadingStateDisable()
            self.outputTab.setImages(images=self.processedImages)
            self.tabWidget.setTabEnabled(1, True)
            self.tabWidget.setCurrentIndex(1)
            self.btnSave.setEnabled(True)
            validations.alert("Model run successfully.", "Information")
            self.btnSave.setStyleSheet("background-color: green")
        except validations.ValidationException as e:
            validations.alert(f"Validation Failed: {str(e)}", "Error")
            print(f"Validation Failed: {str(e)}")
        except Exception as e:
            validations.alert(f"An error occurred: {str(e)}", "Error")
            print(f"An error occurred: {str(e)}")

    def saveImages(self):
        saveDir = QFileDialog.getExistingDirectory(
            self, 'Select Directory to Save Images')
        if saveDir:
            self.saveDirLabel.setText(f'Save directory: {saveDir}')
            for i,image in enumerate(self.processedImages):
                Image.fromarray(image).save(QDir(saveDir).filePath(self.imageFiles[i]))
            validations.alert(f"Saved {len(self.processedImages)} images to {saveDir}", "Information")
            print(f'Saved {len(self.processedImages)} images to {saveDir}')

    def create_memmap(self, size, path='temp.mmap', dtype='uint8', mode='w+'):
        """Creates a np memmap object to store and access large np arrays dynamically from disk. 
        Use this to hold the processed output images."""
        return np.memmap(filename=path, dtype=dtype, mode=mode, shape=size)
    
    def refresh_memmap(self, shape):
        self.outputTab.clearThumbnails()
        self.outputTab.clearImagePreview()
        self.outputTab.images = None
        if self.imageCount != len(self.processedImages) or shape[1] != self.processedImages.shape[1]:
            self.processedImages.resize(shape)
        return

    def load_config(self):
        # Implement your data loading logic here
        print("Loading config data...")
        filePath = QFileDialog.getOpenFileName(self, 'Open Config File', '', 'JSON Files (*.json)')[0]
        if filePath:
            try:
                with open(filePath, 'r') as file:
                    data = json.load(file)
                    self.inputResolutionField.setText(str(data['input_resolution']))
                    self.foveaXField.setText(str(data['fovea_x']))
                    self.foveaYField.setText(str(data['fovea_y']))
                    self.foveaRadiusSlider.setValue(data['fovea_radius'])
                    self.peripheralConeCellsSlider.setValue(data['peripheral_active_cones'])
                    self.foveaRodCellsSlider.setValue(data['fovea_active_rods'])
                    self.peripheralBlurToggle.setChecked(data['peripheral_gaussianBlur'])
                    self.peripheralBlurKernalComboBox.setCurrentText(data['peripheral_gaussianBlur_kernal'])
                    self.peripheralSigmaField.setText(str(data['peripheral_gaussianBlur_sigma']))
                    self.peripheralGrayscaleToggle.setChecked(data['peripheral_grayscale'])
                    self.retinalWarpToggle.setChecked(data['retinal_warp'])
                    self.verboseToggle.setChecked(data['verbose'])
                    self.eyeTypeSingleRadioButton.setChecked(data['eye_type'] == "Single Eye")
                    self.eyeTypeDualRadioButton.setChecked(data['eye_type'] == "Dual Eye")
                    self.foveaTypeStaticRadioButton.setChecked(data['fovea_type'] == "Static")
                    self.foveaTypeDynamicRadioButton.setChecked(data['fovea_type'] == "Dynamic")
            except Exception as e:
                validations.alert(f"An error occurred: {str(e)}", "Error")
                print(f"An error occurred: {str(e)}")
            print("Config Data loaded.")
        else:
            validations.alert("No file path selected.", "Error")
            print("No file path selected.")
    
    def save_config(self):
        # Implement your data saving logic here
        print("Saving data...") 
        filePath = QFileDialog.getSaveFileName(self, 'Save Config File', '', 'JSON Files (*.json)')[0]
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
                    'fovea_type': "Static" if self.foveaTypeStaticRadioButton.isChecked() else "Dynamic"
                }
                with open(filePath, 'w') as file:
                    json.dump(data, file, indent=4)
                validations.alert(f"Config saved at {filePath}", "Information")
            except Exception as e:
                validations.alert(f"An error occurred: {str(e)}", "Error")
                print(f"An error occurred: {str(e)}")
            print("Data saved.")
        else:
            validations.alert("No file path selected.", "Error")
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
            self.foveaRadiusSlider.setEnabled(False)  # Disable if input is not valid

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
    
    # Loading State - Disable all buttons
    def loadingStateEnable(self):
        self.progressBar.reset()
        self.progressBar.setVisible(True)
        for i in range(self.sidebarLayout.count()):
            widget = self.sidebarLayout.itemAt(i).widget()
            if widget is not None:
                self.sidebarLayout.itemAt(i).widget().setEnabled(False)
    
    # Loading State - Enable all buttons
    def loadingStateDisable(self):
        for i in range(self.sidebarLayout.count()):
            widget = self.sidebarLayout.itemAt(i).widget()
            if widget is not None:
                self.sidebarLayout.itemAt(i).widget().setEnabled(True)

def main():
    """EyeballProject's main function."""
    pyApp = QApplication([])
    apply_stylesheet(pyApp, theme='dark_teal.xml')
    pyApp.setStyleSheet(pyApp.styleSheet() + ("QLineEdit { color: white } QComboBox { color: white }"))
    pyAppWindow = EyeballProject()
    pyAppWindow.show()
    sys.exit(pyApp.exec())

if __name__ == "__main__":
    main()