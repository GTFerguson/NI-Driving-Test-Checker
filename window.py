from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLabel
from drivingtestchecker import DrivingTestChecker

WIN_WIDTH = 400
WIN_HEIGHT = 300

# Create the app's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()


        self.setWindowTitle('NI Driving Test Checker')
        self.setFixedSize(QSize(WIN_WIDTH, WIN_HEIGHT))

        pixmap = QPixmap('images/test-drive.png')
        img_label = QLabel(self)
        img_label.setPixmap(pixmap)

        # Resize the image to fit the available space
        img_label.setPixmap(pixmap.scaled(img_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # Set the image as the favicon
        app_icon = QIcon(pixmap)
        self.setWindowIcon(app_icon)        

        # Main vertical layout
        layout = QVBoxLayout(self)
        # Horizontal row
        title_row = QHBoxLayout()
        btn_row = QHBoxLayout()

        # Customize the font of the title label
        font = QFont()
        font.setPointSize(16)  # Set the font size
        font.setBold(True)     # Set the font to bold

        title_label = QLabel('NI Driving Test Checker', self)
        title_label.setFont(font)

        start_btn = QPushButton('Start')
        start_btn.pressed.connect(self.start_checker)
        start_btn.setFixedSize(QSize(100, 40))

        close_btn = QPushButton('Close')
        close_btn.pressed.connect(self.close)
        close_btn.setFixedSize(QSize(100, 40))

        # Add widgets to the title row layout
        title_row.addWidget(img_label)
        title_row.addWidget(title_label)
        title_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add buttons to btn_row layout
        btn_row.addWidget(start_btn)
        btn_row.addWidget(close_btn)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to main layout
        layout.addLayout(title_row)
        layout.addLayout(btn_row)
        layout.setAlignment(start_btn, QtCore.Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)   
        self.show()


    def start_checker(self):
        dtc = DrivingTestChecker()
        dtc.start_checker()


if __name__ == '__main__':
    # Create the app, the main window, and run the app
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()