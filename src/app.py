import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QHBoxLayout, QScrollArea, QGridLayout, QRadioButton, QSlider, QCheckBox, QGroupBox, QTabWidget, QComboBox, QStackedLayout, QLineEdit, QButtonGroup
from PyQt6.QtGui import QPixmap, QIntValidator, QDoubleValidator
from PyQt6.QtCore import QDir, Qt
from PIL import Image, ImageFilter

# Constants
WINDOW_HEIGHT = 1000
WINDOW_WIDTH = 1800
IMAGE_HEIGHT = 500
IMAGE_WIDTH = 500
THUMBNAIL_SIZE = 100
THUMBNAILS_PER_PAGE = 10
THUMBNAILS_PER_ROW = 10


class EyeballProject(QMainWindow):
    """EyeballProject's main window (GUI or view)."""

    def __init__(self):
        super().__init__()
        self.folderPath = ""
        self.images = []
        self.processedImages = []
        self.imageCount = 0
        self.currentThumbnailPage = 0

        self.init_UI()

    def init_UI(self):
        """Initialises UI elements."""
        self.setWindowTitle("Eyeball Project")

        # Main layout and widget
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # region TopLayout
        # Top Layout - houses the folder selector and run model button
        self.topGroup = QGroupBox("Load Dataset")
        topLayout = QHBoxLayout()

        # Button to load images
        self.btnLoad = QPushButton('Load Images')
        self.btnLoad.clicked.connect(self.selectDataset)
        topLayout.addWidget(self.btnLoad, 1)

        # Label to display number of images
        self.imageCountLabel = QLabel('No images selected')
        topLayout.addWidget(self.imageCountLabel, 2)

        # Button to run model
        self.btnRunModel = QPushButton('Run Model')
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

        # Tab widget for input and output images
        self.tabWidget = QTabWidget()
        self.inputTab = QWidget()
        self.outputTab = QWidget()

        # Stacked layout for image previews
        self.inputImageLabel = QLabel('Input preview goes here')
        self.inputImageLabel.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.inputImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inputLayout = QVBoxLayout()
        inputLayout.addWidget(self.inputImageLabel,
                            alignment=Qt.AlignmentFlag.AlignHCenter)
        self.inputTab.setLayout(inputLayout)

        self.outputImageLabel = QLabel('Output preview goes here')
        self.outputImageLabel.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.outputImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outputLayout = QVBoxLayout()
        outputLayout.addWidget(self.outputImageLabel,
                            alignment=Qt.AlignmentFlag.AlignHCenter)
        self.outputTab.setLayout(outputLayout)

        self.tabWidget.addTab(self.inputTab, "Input Image")
        self.tabWidget.addTab(self.outputTab, "Output Image")

        imgViewerLayout.addWidget(self.tabWidget)
        imgViewerGroup.setLayout(imgViewerLayout)
        midLayout.addWidget(imgViewerGroup, 3)

        # Scroll area for thumbnails
        self.scrollArea = QScrollArea()
        self.thumbnailGrid = QGridLayout()
        self.thumbnailGrid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.thumbnailWidget = QWidget()
        self.thumbnailWidget.setLayout(self.thumbnailGrid)
        self.scrollArea.setWidget(self.thumbnailWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFixedHeight(300)
        imgViewerLayout.addWidget(self.scrollArea)

        # Pagination controls
        paginationLayout = QHBoxLayout()
        self.prevPageButton = QPushButton("Previous")
        self.prevPageButton.clicked.connect(self.prevThumbnailPage)
        self.nextPageButton = QPushButton("Next")
        self.nextPageButton.clicked.connect(self.nextThumbnailPage)
        self.pageLabel = QLabel("Page 1", alignment=Qt.AlignmentFlag.AlignCenter)

        paginationLayout.addWidget(self.prevPageButton)
        paginationLayout.addWidget(self.pageLabel)
        paginationLayout.addWidget(self.nextPageButton)
        imgViewerLayout.addLayout(paginationLayout)

        # region Sidebar for image processing parameters
        sidebarLayout = QVBoxLayout()
        sidebarLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebarLayout.setSpacing(10)
        sidebarGroup = QGroupBox("Model Parameters")

        radioLayout = QHBoxLayout()
        self.modeLabel = QLabel("Mode")
        sidebarLayout.addWidget(self.modeLabel)
        self.bwRadioButton = QRadioButton("Black and White")
        self.colorRadioButton = QRadioButton("Color")
        self.colorRadioButton.setChecked(True)
        radioLayout.addWidget(self.bwRadioButton)
        radioLayout.addWidget(self.colorRadioButton)
        sidebarLayout.addLayout(radioLayout)

        self.colorFilterLabel = QLabel("Color Filter")
        sidebarLayout.addWidget(self.colorFilterLabel)
        self.colorFilterComboBox = QComboBox()
        self.colorFilterComboBox.addItems(["None", "Red", "Green", "Blue"])
        sidebarLayout.addWidget(self.colorFilterComboBox)

        self.blurLabel = QLabel("Blur")
        sidebarLayout.addWidget(self.blurLabel)
        self.blurCheckBox = QCheckBox("Blur")
        sidebarLayout.addWidget(self.blurCheckBox)

        # New Inputs in Sidebar
        # Input Resolution
        self.inputResolutionLabel = QLabel("Input Image Resolution (px)")
        self.inputResolutionField = QLineEdit()
        self.inputResolutionField.setPlaceholderText("Enter resolution in format: 300")
        self.intValidator_inputResolutionField = QIntValidator(0, 10000)
        self.inputResolutionField.setValidator(self.intValidator_inputResolutionField)
        sidebarLayout.addWidget(self.inputResolutionLabel)
        sidebarLayout.addWidget(self.inputResolutionField)

        # Fovea Location X, Y
        self.foveaLocationLabel = QLabel("Fovea Location (x, y)")
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
        sidebarLayout.addWidget(self.foveaLocationLabel)
        sidebarLayout.addLayout(foveaLocationLayout)

        # Fovea Radius
        self.foveaRadiusLabel = QLabel("Fovea Radius")
        self.foveaRadiusSlider = QSlider(Qt.Orientation.Horizontal)
        self.foveaRadiusSlider.setRange(1, 100)  # Default range
        self.foveaRadiusSlider.setEnabled(False)  # Disable initially
        self.foveaRadiusValueLabel = QLabel("1")  # Display slider value

        # Layout for slider and value label
        foveaRadiusLayout = QHBoxLayout()
        foveaRadiusLayout.addWidget(self.foveaRadiusSlider)
        foveaRadiusLayout.addWidget(self.foveaRadiusValueLabel)
        sidebarLayout.addWidget(self.foveaRadiusLabel)
        sidebarLayout.addLayout(foveaRadiusLayout)

        # Connect signals to slots
        self.inputResolutionField.textChanged.connect(self.onResolutionChanged)
        self.foveaRadiusSlider.valueChanged.connect(self.onFoveaRadiusChanged)

        # Peripheral Active Cone Cells
        self.peripheralConeCellsLabel = QLabel("Peripheral Active Cone Cells")
        self.peripheralConeCellsSlider = QSlider(Qt.Orientation.Horizontal)
        self.peripheralConeCellsSlider.setRange(0, 100)

        self.peripheralConeCellsValueLabel = QLabel("0%")  # Display slider value

        # Layout for slider and value label
        peripheralConeCellsLayout = QHBoxLayout()
        peripheralConeCellsLayout.addWidget(self.peripheralConeCellsSlider)
        peripheralConeCellsLayout.addWidget(self.peripheralConeCellsValueLabel)

        sidebarLayout.addWidget(self.peripheralConeCellsLabel)
        sidebarLayout.addLayout(peripheralConeCellsLayout)

        # Fovea Active Rod Cells
        self.foveaRodCellsLabel = QLabel("Fovea Active Rod Cells")
        self.foveaRodCellsSlider = QSlider(Qt.Orientation.Horizontal)
        self.foveaRodCellsSlider.setRange(0, 100)

        self.foveaRodCellsValueLabel = QLabel("0%")  # Display slider value

        # Layout for slider and value label
        foveaRodCellsLayout = QHBoxLayout()
        foveaRodCellsLayout.addWidget(self.foveaRodCellsSlider)
        foveaRodCellsLayout.addWidget(self.foveaRodCellsValueLabel)

        sidebarLayout.addWidget(self.foveaRodCellsLabel)
        sidebarLayout.addLayout(foveaRodCellsLayout)

        # Connect signals to slots for updating the value labels
        self.peripheralConeCellsSlider.valueChanged.connect(self.onPeripheralConeCellsChanged)
        self.foveaRodCellsSlider.valueChanged.connect(self.onFoveaRodCellsChanged)


        # Peripheral Gaussian Blur
        self.peripheralBlurToggle = QCheckBox("Peripheral Gaussian Blur")
        self.peripheralBlurToggle.stateChanged.connect(self.onPeripheralBlurToggled)
        sidebarLayout.addWidget(self.peripheralBlurToggle)

        # Peripheral Gaussian Blur Kernal
        self.peripheralBlurKernalLabel = QLabel("Peripheral Gaussian Blur Kernal")
        self.peripheralBlurKernalComboBox = QComboBox()
        self.peripheralBlurKernalComboBox.addItems(
            ["(3,3)", "(5,5)", "(7,7)", "(9,9)", "(11,11)", "(21,21)"])
        self.peripheralBlurKernalLabel.setEnabled(False)
        self.peripheralBlurKernalComboBox.setEnabled(False)
        sidebarLayout.addWidget(self.peripheralBlurKernalLabel)
        sidebarLayout.addWidget(self.peripheralBlurKernalComboBox)

        # Peripheral Gaussian Sigma
        self.peripheralSigmaLabel = QLabel("Peripheral Gaussian Sigma")
        self.peripheralSigmaField = QLineEdit()
        self.peripheralSigmaLabel.setEnabled(False)
        self.peripheralSigmaField.setEnabled(False)

        # Set a validator to allow only float values in the Gaussian Sigma field
        self.floatValidator = QDoubleValidator(0.0, 100.0, 2)
        self.floatValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.peripheralSigmaField.setValidator(self.floatValidator)
        self.peripheralSigmaField.setPlaceholderText("000.00")

        sidebarLayout.addWidget(self.peripheralSigmaLabel)
        sidebarLayout.addWidget(self.peripheralSigmaField)

        # Peripheral Grayscale
        self.peripheralGrayscaleToggle = QCheckBox("Peripheral Grayscale")
        sidebarLayout.addWidget(self.peripheralGrayscaleToggle)

        # Retinal Warp
        self.retinalWarpToggle = QCheckBox("Retinal Warp")
        sidebarLayout.addWidget(self.retinalWarpToggle)

        # Verbose
        self.verboseToggle = QCheckBox("Verbose")
        sidebarLayout.addWidget(self.verboseToggle)

        # Eye Type
        self.eyeTypeLabel = QLabel("Eye Type")
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
        sidebarLayout.addWidget(self.eyeTypeLabel)
        sidebarLayout.addLayout(eyeTypeLayout)

        # Fovea Type
        self.foveaTypeLabel = QLabel("Fovea Type")
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
        sidebarLayout.addWidget(self.foveaTypeLabel)
        sidebarLayout.addLayout(foveaTypeLayout)

        # Add the sidebar to the middle layout
        sidebarGroup.setLayout(sidebarLayout)
        midLayout.addWidget(sidebarGroup, 1)

        # Adding middle layout to main layout
        layout.addLayout(midLayout)
        # endregion MiddleLayout

        # region BottomLayout
        # BottomLayer - Download options
        self.bottomGroup = QGroupBox("Save Options")
        bottomLayout = QHBoxLayout()

        self.btnSave = QPushButton('Save Images')
        self.btnSave.clicked.connect(self.saveImages)
        self.btnSave.setEnabled(False)
        bottomLayout.addWidget(self.btnSave, 1)

        self.saveDirLabel = QLabel('No directory selected')
        bottomLayout.addWidget(self.saveDirLabel, 2)

        self.bottomGroup.setLayout(bottomLayout)
        layout.addWidget(self.bottomGroup)
    # endregion BottomLayout

    # region Event Handlers
    def selectDataset(self):
        folderPath = QFileDialog.getExistingDirectory(
            self, 'Select Folder Containing Images')
        if folderPath:
            dir = QDir(folderPath)
            dir.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.bmp"])
            self.imageFiles = dir.entryList()
            self.imageCount = len(self.imageFiles)
            self.imageCountLabel.setText(
                f'Path: {folderPath}, Images found: {self.imageCount}')

            self.folderPath = folderPath
            self.loadImages(folderPath)
            self.btnRunModel.setEnabled(True)

    def loadImages(self, folderPath):
        self.images = []
        for fileName in self.imageFiles:
            imagePath = QDir(folderPath).filePath(fileName)
            image = Image.open(imagePath)
            self.images.append((fileName, image))

        self.updateThumbnails()

    def updateThumbnails(self):
        # Clear existing thumbnails
        while self.thumbnailGrid.count():
            child = self.thumbnailGrid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        start = self.currentThumbnailPage * THUMBNAILS_PER_PAGE
        end = min(start + THUMBNAILS_PER_PAGE, len(self.images))
        row, col = 0, 0
        for i in range(start, end):
            fileName, image = self.images[i]
            pixmap = QPixmap(QDir(self.folderPath).filePath(fileName)).scaled(
                THUMBNAIL_SIZE, THUMBNAIL_SIZE, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            thumbnailLabel = QLabel()
            thumbnailLabel.setPixmap(pixmap)
            thumbnailLabel.mousePressEvent = lambda event, path=QDir(
                self.folderPath).filePath(fileName): self.setMainImage(path)
            self.thumbnailGrid.addWidget(thumbnailLabel, row, col)
            col += 1
            if col >= THUMBNAILS_PER_ROW:
                col = 0
                row += 1

        self.pageLabel.setText(f"Page {self.currentThumbnailPage + 1}")

    def prevThumbnailPage(self):
        if self.currentThumbnailPage > 0:
            self.currentThumbnailPage -= 1
            self.updateThumbnails()

    def nextThumbnailPage(self):
        if (self.currentThumbnailPage + 1) * THUMBNAILS_PER_PAGE < len(self.images):
            self.currentThumbnailPage += 1
            self.updateThumbnails()

    def setMainImage(self, imagePath):
        pixmap = QPixmap(imagePath).scaled(
            IMAGE_WIDTH, IMAGE_HEIGHT, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.inputImageLabel.setPixmap(pixmap)
        self.tabWidget.setCurrentIndex(0)

    def runModel(self):
        # Process the images based on the selected parameters
        self.processedImages = []
        for fileName, image in self.images:
            if self.bwRadioButton.isChecked():
                image = image.convert("L")  # Convert to black and white
            elif self.colorFilterComboBox.currentText() != "None":
                image = self.applyColorFilter(
                    image, self.colorFilterComboBox.currentText())

            if self.blurCheckBox.isChecked():
                image = image.filter(ImageFilter.GaussianBlur(5))

            self.processedImages.append((fileName, image))

        self.updateOutputThumbnails()
        self.btnSave.setEnabled(True)

    def applyColorFilter(self, image, color):
        # Apply color filter to the image
        r, g, b = image.split()
        if color == "Red":
            r = r.point(lambda i: i * 1.5)
            image = Image.merge("RGB", (r, g, b))
        elif color == "Green":
            g = g.point(lambda i: i * 1.5)
            image = Image.merge("RGB", (r, g, b))
        elif color == "Blue":
            b = b.point(lambda i: i * 1.5)
            image = Image.merge("RGB", (r, g, b))
        return image

    def updateOutputThumbnails(self):
        # Clear existing thumbnails
        while self.thumbnailGrid.count():
            child = self.thumbnailGrid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        start = self.currentThumbnailPage * THUMBNAILS_PER_PAGE
        end = min(start + THUMBNAILS_PER_PAGE, len(self.processedImages))
        row, col = 0, 0
        for i in range(start, end):
            fileName, image = self.processedImages[i]
            thumbnailPath = f"temp_{fileName}"
            image.save(thumbnailPath)
            pixmap = QPixmap(thumbnailPath).scaled(
                THUMBNAIL_SIZE, THUMBNAIL_SIZE, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            thumbnailLabel = QLabel()
            thumbnailLabel.setPixmap(pixmap)
            thumbnailLabel.mousePressEvent = lambda event, path=thumbnailPath: self.setOutputImage(
                path)
            self.thumbnailGrid.addWidget(thumbnailLabel, row, col)
            col += 1
            if col >= THUMBNAILS_PER_ROW:
                col = 0
                row += 1

        self.pageLabel.setText(f"Page {self.currentThumbnailPage + 1}")

        if self.processedImages:
            self.setOutputImage(self.processedImages[0][0])

    def setOutputImage(self, fileName):
        image = None
        for fName, img in self.processedImages:
            if fName == fileName:
                image = img
                break
        if image:
            image.save("temp_output_image.png")
            pixmap = QPixmap("temp_output_image.png").scaled(
                IMAGE_WIDTH, IMAGE_HEIGHT, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            self.outputImageLabel.setPixmap(pixmap)
            self.tabWidget.setCurrentIndex(1)

    def saveImages(self):
        saveDir = QFileDialog.getExistingDirectory(
            self, 'Select Directory to Save Images')
        if saveDir:
            self.saveDirLabel.setText(f'Save directory: {saveDir}')
            for fileName, image in self.processedImages:
                image.save(QDir(saveDir).filePath(fileName))
            print(f'Saved {len(self.processedImages)} images to {saveDir}')

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

# region Main


def main():
    """EyeballProject's main function."""
    pyApp = QApplication([])
    pyAppWindow = EyeballProject()
    pyAppWindow.showMaximized()
    pyAppWindow.show()
    sys.exit(pyApp.exec())


if __name__ == "__main__":
    main()
