from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QScrollArea, QGridLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QDir, Qt
from PIL import ImageQt, Image

IMAGE_HEIGHT = 500
IMAGE_WIDTH = 500
THUMBNAIL_SIZE = 100
THUMBNAILS_PER_PAGE = 10
THUMBNAILS_PER_ROW = 10

class QImagePreview(QWidget):
    def __init__(self, parent=None, folderPath: QDir = None, imageFiles: QDir = None, images:list = None):
        super().__init__(parent)
        self.setupUI()
        self.currentThumbnailPage = 0
        self.folderPath = folderPath if folderPath else None
        self.imageFiles = imageFiles if imageFiles else None
        self.images = images if images else None
        self.imageCount = self.getImageCount()

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Main image display
        self.imagePreviewLabel = QLabel('Preview goes here')
        self.imagePreviewLabel.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.imagePreviewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.imagePreviewLabel)

        # Scroll area for thumbnails
        self.scrollArea = QScrollArea()
        self.thumbnailGrid = QGridLayout()
        self.thumbnailWidget = QWidget()
        self.thumbnailWidget.setLayout(self.thumbnailGrid)
        self.scrollArea.setWidget(self.thumbnailWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFixedHeight(300)
        layout.addWidget(self.scrollArea)

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
        layout.addLayout(paginationLayout)

    def getImageCount(self):
        if self.images:
            return len(self.images)
        elif self.imageFiles:
            return len(self.imageFiles)
        return 0
    
    def updateThumbnails(self):
        # Clear existing thumbnails
        print(self.thumbnailGrid.count())
        while self.thumbnailGrid.count():
            child = self.thumbnailGrid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        start = self.currentThumbnailPage * THUMBNAILS_PER_PAGE
        end = min(start + THUMBNAILS_PER_PAGE, self.imageCount)
        row, col = 0, 0
        for i in range(start, end):
            if self.images is not None:
                image = self.pil_image_to_qimage(self.images[i])
                pixmap = QPixmap.fromImage(image).scaled(
                    THUMBNAIL_SIZE, THUMBNAIL_SIZE, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                
                thumbnailLabel = QLabel()
                thumbnailLabel.setPixmap(pixmap)
                thumbnailLabel.mousePressEvent = lambda x, img=image: self.setInputPreviewImage(image=img)
                self.thumbnailGrid.addWidget(thumbnailLabel, row, col)
                
            else:
                fileName = self.imageFiles[i]
                pixmap = QPixmap(QDir(self.folderPath).filePath(fileName)).scaled(
                    THUMBNAIL_SIZE, THUMBNAIL_SIZE, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            
                thumbnailLabel = QLabel()
                thumbnailLabel.setPixmap(pixmap)
                thumbnailLabel.mousePressEvent = lambda x, path=QDir(self.folderPath).filePath(fileName): self.setInputPreviewImage(path=path)
                self.thumbnailGrid.addWidget(thumbnailLabel, row, col)
            col += 1
            if col >= THUMBNAILS_PER_ROW:
                col = 0
                row += 1

        self.pageLabel.setText(f"Page {self.currentThumbnailPage + 1}")

    def setInputPreviewImage(self, path=None, image=None):
        if path:
            pixmap = QPixmap(path).scaled(IMAGE_WIDTH, IMAGE_HEIGHT, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        else:
            pixmap = QPixmap.fromImage(image).scaled(
                    IMAGE_WIDTH, IMAGE_WIDTH, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.imagePreviewLabel.setPixmap(pixmap)


    def prevThumbnailPage(self):
        if self.currentThumbnailPage > 0:
            self.currentThumbnailPage -= 1
            self.updateThumbnails()

    def nextThumbnailPage(self):
        if (self.currentThumbnailPage + 1) * THUMBNAILS_PER_PAGE < self.imageCount:
            self.currentThumbnailPage += 1
            self.updateThumbnails()

    def setImages(self, images:list):
        self.images = images
        self.imageCount = self.getImageCount() 
        self.updateThumbnails()

    def setImagePath(self, folder:QDir, images:list):
        self.imageFiles = images
        self.folderPath = folder

        self.imageCount = self.getImageCount()
        self.updateThumbnails()

    def pil_image_to_qimage(self, pil_img):
        if pil_img.mode == "RGB":
            r, g, b = pil_img.split()
            pil_img = Image.merge("RGB", (b, g, r))
        elif pil_img.mode == "RGBA":
            r, g, b, a = pil_img.split()
            pil_img = Image.merge("RGBA", (b, g, r, a))

        pil_img = pil_img.convert("RGBA")
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        return qimg