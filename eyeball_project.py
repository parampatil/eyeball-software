import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QHBoxLayout,\
        QScrollArea, QGridLayout, QRadioButton, QSlider, QCheckBox, QGroupBox, QComboBox, QTabWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QDir, Qt
from PIL import Image, ImageFilter
from custom_components import QImagePreview

# Constants
WINDOW_HEIGHT = 1000
WINDOW_WIDTH = 1500
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
        self.imageCount = None
        self.currentThumbnailPage = 0

        self.init_UI()
    
    def init_UI(self):
        """Initialises UI elements."""
        self.setWindowTitle("Eyeball Project")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

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
        self.btnLoad.clicked.connect(self.selectDataset)
        topLayout.addWidget(self.btnLoad,1)

        # Label to display number of images
        self.imageCountLabel = QLabel('No images selected')
        topLayout.addWidget(self.imageCountLabel,2)

        # Button to run model
        self.btnRunModel = QPushButton('Run Model')
        self.btnRunModel.clicked.connect(self.runModel)
        self.btnRunModel.setEnabled(False)
        topLayout.addWidget(self.btnRunModel, 1)
        
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
        #self.tabWidget.setTabEnabled(1,False)
        #endregion Tabs

        # # Label for displaying the main image
        # self.mainImageLabel = QLabel('Preview goes here')
        # self.mainImageLabel.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        # self.mainImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # imgViewerLayout.addWidget(self.mainImageLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        imgViewerGroup.setLayout(imgViewerLayout)
        midLayout.addWidget(imgViewerGroup,3)

        # # Scroll area for thumbnails
        # self.scrollArea = QScrollArea()
        # self.thumbnailGrid = QGridLayout()
        # self.thumbnailGrid.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.thumbnailWidget = QWidget()
        # self.thumbnailWidget.setLayout(self.thumbnailGrid)
        # self.scrollArea.setWidget(self.thumbnailWidget)
        # self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setFixedHeight(300)
        # imgViewerLayout.addWidget(self.scrollArea)

        # # Pagination controls
        # paginationLayout = QHBoxLayout()
        # self.prevPageButton = QPushButton("Previous")
        # self.prevPageButton.clicked.connect(self.prevThumbnailPage)
        # self.nextPageButton = QPushButton("Next")
        # self.nextPageButton.clicked.connect(self.nextThumbnailPage)
        # self.pageLabel = QLabel("Page 1", alignment=Qt.AlignmentFlag.AlignCenter)

        # paginationLayout.addWidget(self.prevPageButton)
        # paginationLayout.addWidget(self.pageLabel)
        # paginationLayout.addWidget(self.nextPageButton)
        # imgViewerLayout.addLayout(paginationLayout)
        
        #region ModelParameters
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

        # Add the sidebar to the middle layout
        sidebarGroup.setLayout(sidebarLayout)
        midLayout.addWidget(sidebarGroup,1)

        # Adding middle layout to main layout
        layout.addLayout(midLayout)
        #endregion MiddleLayout

        #region BottomLayout
        # BottomLayer - Download options
        #TODO
        #endregion BottomLayout


    def selectDataset(self):
        folderPath = QFileDialog.getExistingDirectory(self, 'Select Folder Containing Images')
        if folderPath:
            dir = QDir(folderPath)
            dir.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.bmp"])
            self.imageFiles = dir.entryList()
            self.imageCount = len(self.imageFiles)
            self.imageCountLabel.setText(f'Path: {folderPath}, Images found: {self.imageCount}')

            self.folderPath = folderPath
            self.outputTab.setImagePath(folder=folderPath, images=self.imageFiles)
            self.inputTab.setImagePath(folder=folderPath, images=self.imageFiles)
            #self.inputTab.updateThumbnails()
            self.btnRunModel.setEnabled(True)
            
    # def setupInputTab(self):
    #     layout = QVBoxLayout()
    #     self.inputTab.setLayout(layout)

    #     # Image viewer setup from previous code, adapted for tab
    #     self.mainImageLabel = QLabel('Preview goes here')
    #     self.mainImageLabel.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
    #     self.mainImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     layout.addWidget(self.mainImageLabel)

    #     # Scroll area and thumbnails setup
    #     self.scrollArea = QScrollArea()
    #     self.thumbnailGrid = QGridLayout()
    #     self.thumbnailWidget = QWidget()
    #     self.thumbnailWidget.setLayout(self.thumbnailGrid)
    #     self.scrollArea.setWidget(self.thumbnailWidget)
    #     self.scrollArea.setWidgetResizable(True)
    #     self.scrollArea.setFixedHeight(300)
    #     layout.addWidget(self.scrollArea)

    #     # Pagination controls
    #     paginationLayout = QHBoxLayout()
    #     self.prevPageButton = QPushButton("Previous")
    #     self.prevPageButton.clicked.connect(self.prevThumbnailPage)
    #     self.nextPageButton = QPushButton("Next")
    #     self.nextPageButton.clicked.connect(self.nextThumbnailPage)
    #     self.pageLabel = QLabel("Page 1", alignment=Qt.AlignmentFlag.AlignCenter)

    #     paginationLayout.addWidget(self.prevPageButton)
    #     paginationLayout.addWidget(self.pageLabel)
    #     paginationLayout.addWidget(self.nextPageButton)
    #     layout.addLayout(paginationLayout)

    # def setupOutputTab(self):
    #     layout = QVBoxLayout()
    #     self.inputTab.setLayout(layout)

    #     # Image viewer setup from previous code, adapted for tab
    #     self.mainImageLabel = QLabel('Preview goes here')
    #     self.mainImageLabel.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
    #     self.mainImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     layout.addWidget(self.mainImageLabel)

    #     # Scroll area and thumbnails setup
    #     self.scrollArea = QScrollArea()
    #     self.thumbnailGrid = QGridLayout()
    #     self.thumbnailWidget = QWidget()
    #     self.thumbnailWidget.setLayout(self.thumbnailGrid)
    #     self.scrollArea.setWidget(self.thumbnailWidget)
    #     self.scrollArea.setWidgetResizable(True)
    #     self.scrollArea.setFixedHeight(300)
    #     layout.addWidget(self.scrollArea)

    # def updateThumbnails(self):
    #     # Clear existing thumbnails
    #     while self.thumbnailGrid.count():
    #         child = self.thumbnailGrid.takeAt(0)
    #         if child.widget():
    #             child.widget().deleteLater()

    #     start = self.currentThumbnailPage * THUMBNAILS_PER_PAGE
    #     end = min(start + THUMBNAILS_PER_PAGE, self.imageCount)
    #     row, col = 0, 0
    #     for i in range(start, end):
    #         fileName = self.imageFiles[i]
    #         pixmap = QPixmap(QDir(self.folderPath).filePath(fileName)).scaled(
    #             THUMBNAIL_SIZE, THUMBNAIL_SIZE, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
    #         thumbnailLabel = QLabel()
    #         thumbnailLabel.setPixmap(pixmap)
    #         thumbnailLabel.mousePressEvent = lambda x, path=QDir(self.folderPath).filePath(fileName): self.setInputPreviewImage(path)
    #         self.thumbnailGrid.addWidget(thumbnailLabel, row, col)
    #         col += 1
    #         if col >= THUMBNAILS_PER_ROW:
    #             col = 0
    #             row += 1

    #     self.pageLabel.setText(f"Page {self.currentThumbnailPage + 1}")
        
    # def setInputPreviewImage(self, imagePath):
    #     pixmap = QPixmap(imagePath).scaled(IMAGE_WIDTH, IMAGE_HEIGHT, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
    #     self.mainImageLabel.setPixmap(pixmap)

    # def prevThumbnailPage(self):
    #     if self.currentThumbnailPage > 0:
    #         self.currentThumbnailPage -= 1
    #         self.updateThumbnails()

    # def nextThumbnailPage(self):
    #     if (self.currentThumbnailPage + 1) * THUMBNAILS_PER_PAGE < self.imageCount:
    #         self.currentThumbnailPage += 1
    #         self.updateThumbnails()

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

    def runModel(self):
        # Process the images based on the selected parameters
        self.processedImages = []
        for fileName in self.imageFiles:
            image = Image.open(QDir(self.folderPath).filePath(fileName))
            if self.bwRadioButton.isChecked():
                image = image.convert("L")  # Convert to black and white
            elif self.colorFilterComboBox.currentText() != "None":
                image = self.applyColorFilter(
                    image, self.colorFilterComboBox.currentText())

            if self.blurCheckBox.isChecked():
                image = image.filter(ImageFilter.GaussianBlur(5))

            self.processedImages.append(image)
        
        #self.outputTab.setImages(images=self.processedImages)
        self.outputTab.setImages(images=self.processedImages)
        #self.tabWidget.setTabEnabled(1, True)

def main():
    """EyeballProject's main function."""
    pyApp = QApplication([])
    pyAppWindow = EyeballProject()
    pyAppWindow.show()
    sys.exit(pyApp.exec())

if __name__ == "__main__":
    main()