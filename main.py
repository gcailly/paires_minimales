"""
Application.
"""

# pylint: disable = no-name-in-module, unused-import


import sys
import importlib
import random
from typing import Optional
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QListWidget, QListWidgetItem,
                               QPushButton, QLabel, QWidget, QSpacerItem, QSizePolicy,
                               QDialog, QDialogButtonBox,
                               QMenu, QMenuBar)
from PySide6.QtMultimedia import QSoundEffect


from pairs import pairs


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


class SmoothImageLabel(QLabel):
    """A QLabel subclass that smoothly scales its QPixmap.
    It's needed because the images are 2500x2500 so they have aliasing when they are resized"""

    def __init__(self, image_path: str, width: int, height: int, *args, **kwargs):
        """Initialize the SmoothImageLabel with an image and dimensions."""
        super().__init__(*args, **kwargs)
        self.image_path = image_path
        self.original_pixmap = QPixmap(self.image_path)
        self.current_width = width
        self.current_height = height
        self.set_image(self.image_path, width, height)

    def set_image(self, image_path: str, width: int, height: int):
        """Set the image and resize it according to the given width and height."""
        self.image_path = image_path
        self.current_width = width
        self.current_height = height
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)



class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self):
        """Initialization."""
        super().__init__()

        self.current_sound = None
        self.pairs = pairs  # From 'pairs' package.

        self.setWindowTitle(f"{SoftwareInfo.NAME} {SoftwareInfo.VERSION}")

        # Define the attributes
        self.list_a = None
        self.list_b = None
        self.empty_widget = None
        self.toggle_button = None
        self.left_layout = None
        self.image_label1 = None
        self.image_label2 = None
        self.pixmap1 = None
        self.pixmap2 = None
        self.listen_button = None
        self.right_layout = None
        self.central_widget = None

        self.init_ui()
        self.create_menu()
        self.populate_list_a()

    def create_menu(self):
        """Create the menu."""

        # Create a menu bar for the main window.
        menu_bar = QMenuBar(self)
        # Create a Help menu and add it to the menu bar.
        help_menu = QMenu("Aide", self)
        menu_bar.addMenu(help_menu)
        # Create an About action and add it to the menu bar.
        about_action = menu_bar.addAction("À propos")
        about_action.triggered.connect(self.show_about_dialog)
        # Set the menu bar for the main window.
        self.setMenuBar(menu_bar)

    def init_ui(self):
        """Contains the window's widgets."""

        main_layout = QHBoxLayout()

        # Initialize the lists and button layout.
        self.init_lists_and_button()
        main_layout.addLayout(self.left_layout)

        # Initialize the images and "Listen" button layout.
        self.init_images_and_listen_button()
        main_layout.addLayout(self.right_layout)
        self.init_central_widget(main_layout)
        self.resize_and_position_window()

    def init_lists_and_button(self):
        """Initialize the lists and the toggle button."""

        self.list_a = QListWidget()
        self.list_b = QListWidget()
        self.list_a.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.list_b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.list_a.itemClicked.connect(self.update_list_b)
        self.list_b.itemClicked.connect(self.handle_list_b_click)

        self.empty_widget = QWidget()
        self.empty_widget.setFixedWidth(200)

        self.toggle_button = QPushButton("Afficher/masquer")
        self.toggle_button.clicked.connect(self.toggle_lists)

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.list_a)
        self.left_layout.addWidget(self.list_b)
        self.left_layout.addWidget(self.toggle_button)

        lists_width = self.list_a.sizeHint().width()
        self.toggle_button.setFixedWidth(lists_width)

    def init_images_and_listen_button(self):
        """Initialize the images and the "Listen" button."""

        self.image_label1 = SmoothImageLabel("_transparent.png", 0, 0)
        self.image_label2 = SmoothImageLabel("_transparent.png", 0, 0)
        self.image_label1.setAlignment(Qt.AlignCenter)
        self.image_label2.setAlignment(Qt.AlignCenter)

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.image_label1)
        images_layout.addWidget(self.image_label2)

        self.listen_button = QPushButton("Écouter")
        self.listen_button.setFixedHeight(24)

        listen_button_layout = QHBoxLayout()
        listen_button_layout.addWidget(self.listen_button)
        listen_button_layout.setAlignment(self.listen_button, Qt.AlignCenter)

        self.right_layout = QVBoxLayout()
        self.right_layout.addLayout(images_layout)
        self.right_layout.addLayout(listen_button_layout)

    def init_central_widget(self, main_layout):
        """Create the central widget and set the main layout."""

        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def resize_and_position_window(self):
        """Resize and position the main window."""

        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()

        desired_width = int(screen_size.width() * 0.8)
        desired_height = int(screen_size.height() * 0.8)

        self.resize(desired_width, desired_height)
        self.resize_images()

    def resize_images(self):
        """Resize the images when the window is resized."""

        # Available width and height for the images.
        available_width = self.width() - self.list_a.width()

        # Main window height - "Listen" button height - margins.
        available_height = (self.height() - self.listen_button.height()
                        - self.layout().contentsMargins().top()
                        - self.layout().contentsMargins().bottom())

        # Use 60% of the available width and heigh for each image.
        width = int(available_width * 0.6)
        height = int(available_height * 0.6)

        # Resize the images based on the window size.
        self.image_label1.set_image(self.image_label1.image_path, width, height)
        self.image_label2.set_image(self.image_label2.image_path, width, height)

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

    def populate_list_a(self):
        """Populate the first list (A) with pair category ("p / b", etc.)."""
        for pair in self.pairs:
            item = QListWidgetItem(pair[0].replace("_", " / "))
            self.list_a.addItem(item)

    def update_list_b(self, item):
        """Update the second list (B) with pairs of a category ("pain / bain", etc.)."""
        # Find the corresponding pair.
        pair_label = item.text().replace(" / ", "_")
        pair_data = None
        for pair in self.pairs:
            if pair[0] == pair_label:
                pair_data = pair[1:]
                break
        # Clear List B and update it with the new word pairs.
        if pair_data:
            self.list_b.clear()
            for word_pair in pair_data:
                formatted_pair = f"{word_pair[0]} / {word_pair[1]}"
                self.list_b.addItem(formatted_pair)

    def handle_list_b_click(self, item):
        """Handle the click event on a word pair in List B. Update the displayed images and prepare
        the audio file to be played by the "Listen" button."""

        # Get the image names and audio file from the clicked item in List B.
        pair = item.text().split(" / ")
        word1, word2 = pair
        image1_path = PathManager.get_image_path(word1)
        image2_path = PathManager.get_image_path(word2)
        audio_files = [
            PathManager.get_sound_path(word1),
            PathManager.get_sound_path(word2)]

        # Update the image labels with the new images.
        self.image_label1.set_image(image1_path, 0, 0)
        self.image_label2.set_image(image2_path, 0, 0)

        self.resize_images()

        # Update the audio playback function of the "Listen" button.
        self.listen_button.clicked.connect(lambda: self.play_random_audio(audio_files))

    def play_random_audio(self, audio_files):
        """Play a random audio file from the given list of audio files."""
        random_audio = random.choice(audio_files)
        self.current_sound = QSoundEffect()
        self.current_sound.setSource(QUrl.fromLocalFile(random_audio))
        # self.current_sound.setVolume(0.5)
        self.current_sound.play()

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
