"""
Application.
"""

# pylint: disable = no-name-in-module, unused-import


import sys
import importlib
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QScreen
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QListWidget,
                               QPushButton, QLabel, QWidget, QSpacerItem, QSizePolicy,
                               QDialog, QDialogButtonBox, QMenu, QMenuBar)




class SoftwareInfo:
    """
    Defines the general information about the software, including the name, version, author, and
    associated website.
    """
    NAME = "Les Paires Minimales"
    VERSION = "1.0.0"
    AUTHOR = "Gautier Cailly"
    WEBSITE = "www.oortho.fr"





class PathManager:
    """
    Provides static methods for obtaining the paths to image and sound files corresponding to a
    given word.
    """

    @staticmethod
    def get_image_path(word: str) -> Path:
        """Gets the path to the image file corresponding to the given word."""
        with importlib.resources.path("data.images", f"{word}.png") as image_path:
            return image_path

    @staticmethod
    def get_sound_path(word: str) -> Path:
        """Gets the path to the sound file corresponding to the given word."""
        with importlib.resources.path("data.sounds", f"{word}.wav") as sound_path:
            return sound_path



class AboutDialog(QDialog):
    """
    Creates and displays an about window with information about the software, author, and
    image credits.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initializes the user interface of the dialog."""

        self.setWindowTitle("About")
        self.setMinimumWidth(300)
        layout = QVBoxLayout()

        # Create content.
        content_text = f"""
            <b>{SoftwareInfo.NAME}
            </b><br>
            Version : {SoftwareInfo.VERSION}
            <br>
            Auteur : {SoftwareInfo.AUTHOR}
            <br>
            <a href="https://www.oortho.fr">www.oortho.fr</a><br> <br>
            Crédit images : ARASAAC, Gautier Cailly
            <br>
            <br>
            This is a sample paragraph of text.
            Voilà.
            """
        content = QLabel(content_text)
        content.setWordWrap(True)
        layout.addWidget(content)

        # Create action buttons.
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def show(self):
        """Displays the modal dialog."""
        self.exec()


class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self):
        """Initialization."""
        super().__init__()
        self.setWindowTitle(f"{SoftwareInfo.NAME} {SoftwareInfo.VERSION}")
        self.create_menu()
        self.init_ui()

    def create_menu(self):
        """Create the menu."""

        menu_bar = QMenuBar(self)

        help_menu = QMenu("Help", self)
        menu_bar.addMenu(help_menu)

        about_action = menu_bar.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)

        self.setMenuBar(menu_bar)


    def init_ui(self):
        """Contains the window's widgets."""

        # Create the main layout.
        main_layout = QHBoxLayout()

        # Create lists A and B.
        self.list_a = QListWidget()
        self.list_b = QListWidget()
        self.list_a.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.list_b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Widget with the same width as the lists to replace them when they are hidden.
        self.empty_widget = QWidget()
        self.empty_widget.setFixedWidth(200)

        # Create the button to hide/show the lists.
        self.toggle_button = QPushButton("Hide/Show")
        self.toggle_button.clicked.connect(self.toggle_lists)
        # self.toggle_button.setFixedSize(100, 30)  # Set a fixed size for the button.

        # Create a QVBoxLayout for the lists and the button.
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.list_a)
        self.left_layout.addWidget(self.list_b)
        self.left_layout.addWidget(self.toggle_button)
        lists_width = self.list_a.sizeHint().width()
        self.toggle_button.setFixedWidth(lists_width)

        # Create the two images side by side.
        self.image_label1 = QLabel()
        self.image_label2 = QLabel()
        self.pixmap1 = QPixmap("image1.png")
        self.pixmap2 = QPixmap("image2.png")
        self.image_label1.setPixmap(self.pixmap1)
        self.image_label2.setPixmap(self.pixmap2)
        self.image_label1.setAlignment(Qt.AlignCenter)
        self.image_label2.setAlignment(Qt.AlignCenter)

        # Create a QHBoxLayout for the images.
        images_layout = QHBoxLayout()
        images_layout.addWidget(self.image_label1)
        images_layout.addWidget(self.image_label2)

        # Create the "Listen" button.
        self.listen_button = QPushButton("Listen")
        self.listen_button.setFixedHeight(24)

        # Create a QHBoxLayout to center the "Listen" button.
        listen_button_layout = QHBoxLayout()
        listen_button_layout.addWidget(self.listen_button)
        listen_button_layout.setAlignment(self.listen_button, Qt.AlignCenter)

        # Add the images and the button to a QVBoxLayout.
        right_layout = QVBoxLayout()
        right_layout.addLayout(images_layout)  # Add the QHBoxLayout of images here.
        right_layout.addLayout(listen_button_layout)  # Add the QHBoxLayout of the "Listen" button.

        # Add the left and right layouts to the main layout.
        main_layout.addLayout(self.left_layout)
        main_layout.addLayout(right_layout)

        # Fixed width for the lists and the button.
        fixed_width = 200
        self.list_a.setFixedWidth(fixed_width)
        self.list_b.setFixedWidth(fixed_width)
        self.toggle_button.setFixedWidth(fixed_width)

        # Create a central widget and set the main layout.
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        # Get the screen size.
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()

        # Calculate the desired size as 80% of the screen's width and height
        desired_width = int(screen_size.width() * 0.8)
        desired_height = int(screen_size.height() * 0.8)

        # Set the size of the main window.
        self.resize(desired_width, desired_height)
        # self.showMaximized()
        self.resize_images()


    def resize_images(self):
        """Resize the images when the window is resized."""

        # Available width and height for the images.
        available_width = self.width() - self.list_a.width()

        # Main window height - "Listen" button height - margins.
        available_height = (self.height() - self.listen_button.height()
                           - self.layout().contentsMargins().top()
                           - self.layout().contentsMargins().bottom())
        print(f"""
            available_height : {available_height}
            self.height() : {self.height()}
            self.toggle_button.height() : {self.listen_button.height()}
            self.layout().contentsMargins().top() : {self.layout().contentsMargins().top()}
            self.layout().contentsMargins().bottom() : {self.layout().contentsMargins().bottom()}
        """)

        # Use 60% of the available width and heigh for each image.
        width = int(available_width * 0.6)
        height = int(available_height * 0.6)

        # Resize the images based on the window size.
        self.image_label1.setPixmap(self.pixmap1.scaled(width, height, Qt.KeepAspectRatio))
        self.image_label2.setPixmap(self.pixmap2.scaled(width, height, Qt.KeepAspectRatio))


    def resizeEvent(self, event):
        """Handle the window resize event."""

        super().resizeEvent(event)
        self.resize_images()


    def toggle_lists(self):
        """Toggle the visibility of the lists. Replace them with an empty widget to take the same
        place/size."""

        # Check if List A is visible.
        if self.list_a.isVisible():
            # Get the index of List A in the left layout.
            left_layout_index = self.left_layout.indexOf(self.list_a)
            # Remove List A and List B from the left layout.
            self.left_layout.removeWidget(self.list_a)
            self.left_layout.removeWidget(self.list_b)
            # Hide List A and List B.
            self.list_a.hide()
            self.list_b.hide()
            # Insert the empty widget at the index of List A.
            self.left_layout.insertWidget(left_layout_index, self.empty_widget)
            # Show the empty widget.
            self.empty_widget.show()
        else:
            # Get the index of the empty widget in the left layout.
            left_layout_index = self.left_layout.indexOf(self.empty_widget)
            # Remove the empty widget from the left layout.
            self.left_layout.removeWidget(self.empty_widget)
            # Hide the empty widget.
            self.empty_widget.hide()
            # Insert List A and List B at the index of the empty widget.
            self.left_layout.insertWidget(left_layout_index, self.list_a)
            self.left_layout.insertWidget(left_layout_index + 1, self.list_b)
            # Show List A and List B.
            self.list_a.show()
            self.list_b.show()

    def show_about_dialog(self):
        """Display an About Dialog for the application."""

        # Create an instance of the AboutDialog.
        about_dialog = AboutDialog()
        # Show the AboutDialog.
        about_dialog.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
