"""
Application.
"""

# pylint: disable = no-name-in-module, unused-import, invalid-name, attribute-defined-outside-init


import sys
import importlib.resources
import random
from typing import Optional
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QAction, QActionGroup, QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QMessageBox, QWidgetAction,
                               QListWidget, QListWidgetItem, QCheckBox,
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
    VERSION = "0.5.0"
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
        file_path = importlib.resources.files("data") / "images" / f"{word}.png"
        return file_path

    @staticmethod
    def get_sound_path(word: str) -> Path:
        """Gets the path to the sound file corresponding to the given word."""
        file_path = importlib.resources.files("data") / "sounds" / f"{word}.wav"
        return file_path

    @staticmethod
    def file_exists(file_path: Path) -> None:
        """Checks if a file exists at the given path."""
        if not file_path.exists():
            print(f"{file_path} does not exist.")


class CurrentItem:
    """Store current item info."""

    def __init__(self, word1: str, word2: str, audio: str):
        """Init."""

        self.word1 = word1
        self.word2 = word2
        self.audio = audio
        self.score = 0
        self.total_attempts = 0


class AboutDialog(QDialog):
    """
    Creates and displays an about window with information about the software, author, and
    image credits.
    """

    def __init__(self,
                 app_name: str, app_version: str, app_author: str, website: str,
                 parent=None):
        """Init."""

        super().__init__(parent)
        self.app_name = app_name
        self.app_version = app_version
        self.app_author = app_author
        self.website = website
        self.init_ui()

    def init_ui(self):
        """Initializes the user interface of the dialog."""

        self.setWindowTitle("À propos")
        self.setMinimumWidth(300)
        layout = QVBoxLayout()

        # Create content.
        content_text = f"""
            <b>{self.app_name}
            </b><br>
            Version : {self.app_version}
            <br>
            Auteur : {self.app_author}
            <br>
            <a href="https://{self.website}">{self.website}</a>
            """
        content = QLabel(content_text)
        content.setWordWrap(True)
        content.setOpenExternalLinks(True)
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
    It's needed because big images are aliased when they are resized smaller."""

    def __init__(self, image_path: str, width: int, height: int, *args, **kwargs):
        """Initialize the SmoothImageLabel with an image and dimensions."""
        super().__init__(*args, **kwargs)
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)
        self.width = width
        self.height = height
        self.set_image(self.image_path, self.width, self.height)

    def set_image(self, image_path: str, width: int, height: int):
        """Set the image and resize it according to the given width and height."""
        self.image_path = image_path
        self.width = width
        self.height = height
        self.pixmap = QPixmap(self.image_path)
        self.pixmap = self.pixmap.scaled(self.width, self.height,
                                         Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)


class CheckBoxMenuItem(QWidget):
    """A custom menu item with a checkbox.
    Rationale: the menu does not close when the checkbox is clicked. Very handy for options."""

    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.checkbox = QCheckBox(text, self)
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self):
        """Initialization."""
        super().__init__()

        self.current_sound = None
        self.current_item = None
        self.pairs = pairs  # From 'pairs' package.

        self.setWindowTitle(f"{SoftwareInfo.NAME} {SoftwareInfo.VERSION}")
        icon_path = importlib.resources.files("data") / "app_icon.png"
        icon = QIcon(str(icon_path))
        self.setWindowIcon(icon)

        # Define the attributes.
        self.list_a = None
        self.list_b = None
        self.toggle_button = None
        self.left_layout = None
        self.image_label1 = None
        self.image_label2 = None
        self.pixmap1 = None
        self.pixmap2 = None
        self.listen_button = None
        self.next_button = None
        self.central_widget = None

        self.init_ui()
        self.populate_list_a()

    def init_ui(self):
        """Contains the window's widgets."""

        # Menu creation.
        self.init_menu()

        main_layout = QHBoxLayout()

        self.left_layout = self.init_left_layout()
        self.right_layout = self.init_right_layout()
        main_layout.addLayout(self.left_layout)
        main_layout.addLayout(self.right_layout)

        # Initialize the images and "Listen" button layout.
        self.init_central_widget(main_layout)
        self.resize_and_position_window()

    def init_menu(self):
        """Create the menu."""

        # Create a menu bar for the main window.
        menu_bar = QMenuBar(self)

        # Create menu "Options".
        options_menu = QMenu("Options", self)
        menu_bar.addMenu(options_menu)
        
        # FIXME : CheckBoxMenuItem devrait directement être un QWidgetAction, avec une option setChecked, etc.
        # Create a custom widget with a QCheckBox for the "Random Item" option.
        self.opt_random = CheckBoxMenuItem("Ordre aléatoire", self)
        self.opt_random.checkbox.setChecked(True)
        # Create a QWidgetAction, set the custom widget, and add it to the "Options" menu.
        random_widget_action = QWidgetAction(self)
        random_widget_action.setDefaultWidget(self.opt_random)
        options_menu.addAction(random_widget_action)
        
        # Create a custom widget with a QCheckBox for the "Automatic Listening" option.
        self.opt_auto_listen = CheckBoxMenuItem("Écoute automatique", self)
        self.opt_auto_listen.checkbox.setChecked(True)
        # Create a QWidgetAction, set the custom widget, and add it to the "Options" menu.
        auto_listen_widget_action = QWidgetAction(self)
        auto_listen_widget_action.setDefaultWidget(self.opt_auto_listen)
        options_menu.addAction(auto_listen_widget_action)

        # Create a Help menu and add it to the menu bar.
        help_menu = QMenu("Aide", self)
        menu_bar.addMenu(help_menu)
        # Create an About action and add it to the menu bar.
        about_action = menu_bar.addAction("À propos")
        about_action.triggered.connect(self.show_about_dialog)
        # Set the menu bar for the main window.
        self.setMenuBar(menu_bar)

    def init_left_layout(self):
        """Initialize the lists and the toggle button."""

        self.list_a = QListWidget()
        self.list_b = QListWidget()
        self.list_a.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.list_b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.list_a.itemClicked.connect(self.update_list_b)
        self.list_b.itemClicked.connect(self.handle_list_b_click)

        self.toggle_button = QPushButton("Afficher/masquer")
        self.toggle_button.clicked.connect(self.toggle_lists)

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.list_a)
        self.left_layout.addWidget(self.list_b)
        self.left_layout.addWidget(self.toggle_button, alignment=Qt.AlignBottom)

        lists_width = self.list_a.sizeHint().width()
        self.toggle_button.setFixedWidth(lists_width)

        return self.left_layout

    def init_right_layout(self):
        """Initialize the images and the "Listen" button."""

        image_null = PathManager.get_image_path("_null")
        self.image_label1 = SmoothImageLabel(image_null, 10, 10)
        self.image_label2 = SmoothImageLabel(image_null, 10, 10)
        self.image_label1.setAlignment(Qt.AlignCenter)
        self.image_label2.setAlignment(Qt.AlignCenter)
        self.image_label1.mousePressEvent = self.image_label1_clicked
        self.image_label2.mousePressEvent = self.image_label2_clicked

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.image_label1)
        images_layout.addWidget(self.image_label2)

        self.listen_button = QPushButton("Écouter")
        self.listen_button.setFixedHeight(32)
        self.next_button = QPushButton(" > ")
        self.next_button.setFixedHeight(32)
        self.next_button.clicked.connect(self.next_item)

        listen_button_layout = QHBoxLayout()
        listen_button_layout.addStretch()
        listen_button_layout.addWidget(self.listen_button)
        listen_button_layout.addWidget(self.next_button)

        listen_button_layout.setAlignment(self.listen_button, Qt.AlignCenter)
        listen_button_layout.addStretch()

        init_right_layout = QVBoxLayout()
        init_right_layout.addStretch(2)
        init_right_layout.addLayout(images_layout)
        init_right_layout.addStretch(1)
        init_right_layout.addLayout(listen_button_layout)
        init_right_layout.addStretch(2)

        return init_right_layout

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
        """Toggle the visibility of the lists."""

        # Empty widget to take the same place/size.
        empty_widget = QWidget()
        empty_widget.setFixedWidth(200)

        # Check if List A is visible.
        if self.list_a.isVisible():
            self.list_a.hide()
            self.list_b.hide()
            self.left_layout.insertWidget(0, empty_widget)
            empty_widget.show()
        else:
            self.left_layout.removeWidget(empty_widget)
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

        # Select the first item in List B automatically.
        if self.list_b.count() > 0:
            first_item = self.list_b.item(0)
            self.list_b.setCurrentItem(first_item)
            self.handle_list_b_click(first_item)

    def handle_list_b_click(self, item):
        """Handle the click event on a word pair in List B. Update the displayed images and prepare
        the audio file to be played by the "Listen" button."""

        # Get the image and audio names from the clicked item in List B.
        pair = item.text().split(" / ")
        word1, word2 = pair
        # Pick a random word as good response, which will be pronounced (audio).
        audio = random.choice(pair)
        # Store this in current item.
        self.current_item = CurrentItem(word1, word2, audio)
        # Set paths.
        audio_path = PathManager.get_sound_path(audio)
        image1_path = PathManager.get_image_path(word1)
        image2_path = PathManager.get_image_path(word2)

        # Update the image labels with the new images.
        self.image_label1.set_image(image1_path, 0, 0)
        self.image_label2.set_image(image2_path, 0, 0)
        self.resize_images()
        # Update the audio playback function of the "Listen" button.
        self.listen_button.clicked.connect(lambda: self.play_audio(audio_path))

        # Play the audio automatically if the "Automatic Listening" option is checked.
        if self.opt_auto_listen.checkbox.isChecked():
            self.play_audio(audio_path)

    def image_label1_clicked(self, event):
        """When Image1 is clicked."""
        self.event = event
        self.check_answer(self.current_item.word1)

    def image_label2_clicked(self, event):
        """When Image2 is clicked."""
        self.event = event
        self.check_answer(self.current_item.word2)

    def check_answer(self, selected_word):
        """Check if clicked image corresponds to audio."""

        if not self.current_item:
            return None

        correct_word = self.current_item.audio

        if selected_word == correct_word:
            self.current_item.score += 1
            QMessageBox.information(self, "Bravo!", f"La réponse est correcte: {correct_word}")
            self.next_item()
            # If "Automatic Listening" is checked, play the audio for the next item automatically.
            if self.opt_auto_listen.checkbox.isChecked():
                audio_path = PathManager.get_sound_path(self.current_item.audio)
                self.play_audio(audio_path)
        else:
            QMessageBox.warning(self, "Erreur", f"La réponse est incorrecte. La bonne réponse est: {correct_word}")

        self.current_item.total_attempts += 1

    def next_item(self):
        """Go to next item : next in list B or random in list B.
        It depends on the random order option."""

        # If nothing is selected in list B, do nothing.
        if self.list_b.currentRow() == -1:
            return

        if self.opt_random.checkbox.isChecked():
            current_row = self.list_b.currentRow()
            new_row = current_row

            # Chooses a new random row different from the current one.
            while new_row == current_row:
                new_row = random.randint(0, self.list_b.count() - 1)

            self.list_b.setCurrentRow(new_row)
        else:
            # If the current item is the last one, loop back to the first item.
            if self.list_b.currentRow() == self.list_b.count() - 1:
                self.list_b.setCurrentRow(0)
            else:
                # Otherwise, just move to the next item.
                self.list_b.setCurrentRow(self.list_b.currentRow() + 1)

        self.list_b.itemClicked.emit(self.list_b.currentItem())

    def play_audio(self, file: Path):
        """Play a random audio file from the given list of audio files.
        WARNING : Add this line into the __init__ of the QMainWindow, else sound will be stopped
        when the function ends (so fast we won't hear anything).
            self.current_sound = None
        """
        self.current_sound = QSoundEffect()
        self.current_sound.setSource(QUrl.fromLocalFile(file))
        self.current_sound.setVolume(1)
        self.current_sound.play()

    def show_about_dialog(self):
        """Display an About Dialog for the application."""

        # Create an instance of the AboutDialog.
        about_dialog = AboutDialog(parent = self,
                                   app_name=SoftwareInfo.NAME,
                                   app_version=SoftwareInfo.VERSION,
                                   app_author=SoftwareInfo.AUTHOR,
                                   website=SoftwareInfo.WEBSITE)
        # Show the AboutDialog.
        about_dialog.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
