import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QHBoxLayout,\
        QScrollArea, QGridLayout, QRadioButton, QSlider, QCheckBox, QGroupBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QDir, Qt
 
# Constants
WINDOW_HEIGHT = 1000
WINDOW_WIDTH = 1500
IMAGE_HEIGHT = 500
IMAGE_WIDTH = 500

class EyeballProject(QMainWindow):
    """EyeballProject's main window (GUI or view)."""

    def __init__(self):
        super().__init__()
        self.folderPath = ""
        self.images = []
        self.imageCount = None

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
        
        # Adding top layout to main layout
        self.topGroup.setLayout(topLayout)
        layout.addWidget(self.topGroup)
        #endregion TopLayout

        #region MiddleLayout
        # Middle Layout - houses the image viewer and processing parameters
        midLayout = QHBoxLayout()

        imgViewerLayout = QVBoxLayout()
        imgViewerGroup = QGroupBox("Image Preview")

        # Label for displaying the main image
        self.mainImageLabel = QLabel('Preview goes here')
        self.mainImageLabel.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.mainImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        imgViewerLayout.addWidget(self.mainImageLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        imgViewerGroup.setLayout(imgViewerLayout)
        midLayout.addWidget(imgViewerGroup,3)

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
        
        # Sidebar for image processing parameters
        sidebarLayout = QVBoxLayout()
        sidebarGroup = QGroupBox("Model Parameters")
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        sidebarLayout.addWidget(slider)

        checkbox = QCheckBox("Enable Option")
        sidebarLayout.addWidget(checkbox)

        radio1 = QRadioButton("Option 1")
        radio2 = QRadioButton("Option 2")
        sidebarLayout.addWidget(radio1)
        sidebarLayout.addWidget(radio2)

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
            self.loadImages(folderPath)
            
    def loadImages(self, folderPath):
        # Clear existing thumbnails
        while self.thumbnailGrid.count():
            child = self.thumbnailGrid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Display thumbnails in 2 rows x 10 columns
        row, col = 0, 0
        for i, fileName in enumerate(self.imageFiles[:(20 if len(self.imageFiles) > 20 else -1)]): 
            imagePath = QDir(folderPath).filePath(fileName)
            pixmap = QPixmap(imagePath).scaled(100, 100, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            thumbnailLabel = QLabel()
            thumbnailLabel.setPixmap(pixmap)
            thumbnailLabel.mousePressEvent = lambda event, path=imagePath: self.setMainImage(path)
            self.thumbnailGrid.addWidget(thumbnailLabel, row, col)
            col += 1
            if col >= 10:
                col = 0
                row += 1
                if row >= 2:
                    break  
        
    def setMainImage(self, imagePath):
        pixmap = QPixmap(imagePath).scaled(IMAGE_WIDTH, IMAGE_HEIGHT, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.mainImageLabel.setPixmap(pixmap)

def main():
    """EyeballProject's main function."""
    pyApp = QApplication([])
    pyAppWindow = EyeballProject()
    pyAppWindow.show()
    sys.exit(pyApp.exec())

if __name__ == "__main__":
    main()