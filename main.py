"""
Application.
"""

# pylint: disable = no-name-in-module, unused-import, invalid-name, attribute-defined-outside-init


import sys
import json
import importlib.resources
import random
import time
import os
import platform
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QWidgetAction,
                               QListWidget, QListWidgetItem, QCheckBox,
                               QPushButton, QLabel, QWidget, QSizePolicy,
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
    VERSION = "1.0.3"
    AUTHOR = "Gautier Cailly"
    WEBSITE = "www.oortho.fr"


class PathManager:
    """
    Provides static methods for obtaining the paths to image and sound files corresponding to a
    given word.
    """

    manual_path = importlib.resources.files("data") / "manuel.pdf"

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
                 info=None, parent=None):
        """Init."""

        super().__init__(parent)
        self.app_name = app_name
        self.app_version = app_version
        self.app_author = app_author
        self.website = website
        self.info = info
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
        if self.info is not None:
            content_text += f"""
                <br><br>
                {self.info}
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


class OptionsManager:
    """Manage option's loading and saving."""

    def __init__(self, file_path):
        """Initialize the OptionsManager with the given file path."""
        self.file_path = file_path
        self.options = self.load_options()

    def load_options(self):
        """Load options from the JSON file or create default options."""
        # Check if the options file exists.
        if Path(self.file_path).is_file():
            # Load options from the file.
            with open(self.file_path, "r", encoding="utf-8") as file:
                options = json.load(file)
        else:
            # Create default options if the file doesn't exist.
            options = {"random_order": True,
                       "auto_listen": True,
                       "success_sound": True,
                       "hide_next_button": True}
        return options

    def save_options(self):
        """Save the current options to the JSON file."""
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.options, file)

    def get_option(self, key, default=None):
        """Get the value of the specified option.
        default is for when an option is not available in the json file."""
        return self.options.get(key, default)

    def set_option(self, key, value):
        """Set the value of the specified option."""
        self.options[key] = value


class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self):
        """Initialization."""
        super().__init__()

        self.current_sound = QSoundEffect()
        self.current_item = None
        self.pairs = pairs  # From 'pairs' package.

        # Set title and icon.
        self.setWindowTitle(f"{SoftwareInfo.NAME} {SoftwareInfo.VERSION}")
        icon_path = importlib.resources.files("data") / "app_icon.png"
        icon = QIcon(str(icon_path))
        self.setWindowIcon(icon)

        # Define the attributes.
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
        self.next_button = None
        self.central_widget = None

        # Create UI.
        self.init_ui()
        self.populate_list_a()
        self.load_options_from_file()

    def load_options_from_file(self):
        """Loads options from the json options file and apply them."""
        # Load options.
        # Set up OptionsManager and get checkboxes state.
        self.options_manager = OptionsManager("options.json")
        self.opt_random.checkbox.setChecked(
            self.options_manager.get_option("random_order", True))
        self.opt_auto_listen.checkbox.setChecked(
            self.options_manager.get_option("auto_listen", True))
        self.opt_success_sound.checkbox.setChecked(
            self.options_manager.get_option("success_sound", True))
        self.opt_hide_next_button.checkbox.setChecked(
            self.options_manager.get_option("hide_next_button", True))

        # Apply options.
        # Handle Hide Next Button option.
        self.toggle_hide_next_button(state=self.opt_hide_next_button.checkbox.isChecked())

    def init_ui(self):
        """Contains the window's widgets."""

        # Menu creation. Make it first because it loads options. They are be applied when layouts of
        # main windows are initialized.
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

        # FIXME : These redundant groups of 6 lines for each CheckBoxMenuItem should be factorized.
        # These 6 lines are complex because this is a custom widget.

        # Create a custom widget with a QCheckBox for the "Random Item" option.
        self.opt_random = CheckBoxMenuItem("Ordre aléatoire", self)
        self.opt_random.checkbox.setChecked(True)
        self.opt_random.checkbox.stateChanged.connect(self.save_options_to_file)
        # Create a QWidgetAction, set the custom widget, and add it to the "Options" menu.
        random_widget_action = QWidgetAction(self)
        random_widget_action.setDefaultWidget(self.opt_random)
        options_menu.addAction(random_widget_action)

        # Create a custom widget with a QCheckBox for the "Automatic Listening" option.
        self.opt_auto_listen = CheckBoxMenuItem("Écoute automatique", self)
        self.opt_auto_listen.checkbox.setChecked(True)
        self.opt_auto_listen.checkbox.stateChanged.connect(self.save_options_to_file)
        # Create a QWidgetAction, set the custom widget, and add it to the "Options" menu.
        auto_listen_widget_action = QWidgetAction(self)
        auto_listen_widget_action.setDefaultWidget(self.opt_auto_listen)
        options_menu.addAction(auto_listen_widget_action)

        # Create a custom widget with a QCheckBox for the "Success Sound" option.
        self.opt_success_sound = CheckBoxMenuItem("Son de réussite", self)
        self.opt_success_sound.checkbox.setChecked(True)
        self.opt_success_sound.checkbox.stateChanged.connect(self.save_options_to_file)
        # Create a QWidgetAction, set the custom widget, and add it to the "Options" menu.
        success_sound_widget_action = QWidgetAction(self)
        success_sound_widget_action.setDefaultWidget(self.opt_success_sound)
        options_menu.addAction(success_sound_widget_action)

        # Create a custom widget with a QCheckBox for the "Hide Next Button" option.
        self.opt_hide_next_button = CheckBoxMenuItem('Cacher le bouton "Suivant"', self)
        self.opt_hide_next_button.checkbox.setChecked(True)
        self.opt_hide_next_button.checkbox.stateChanged.connect(self.save_options_to_file)
        # Create a QWidgetAction, set the custom widget, and add it to the "Options" menu.
        opt_hide_next_button_widget_action = QWidgetAction(self)
        opt_hide_next_button_widget_action.setDefaultWidget(self.opt_hide_next_button)
        options_menu.addAction(opt_hide_next_button_widget_action)
        # Action when un/checked.
        self.opt_hide_next_button.checkbox.stateChanged.connect(self.toggle_hide_next_button)

        # Create a Help menu and add it to the menu bar.
        help_action = menu_bar.addAction("Manuel")
        help_action.triggered.connect(lambda: self.open_pdf(PathManager.manual_path))
        # Create an About action and add it to the menu bar.
        about_action = menu_bar.addAction("À propos")
        about_action.triggered.connect(self.show_about_dialog)
        # Set the menu bar for the main window.
        self.setMenuBar(menu_bar)

    def init_left_layout(self):
        """Initialize the lists and the toggle button."""

        # Empty widget to take the same place/size than list A/B.
        self.empty_widget = QWidget()
        self.empty_widget.setFixedWidth(200)
        self.empty_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.empty_widget.hide()
        self.list_a = QListWidget()
        self.list_a.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.list_a.itemClicked.connect(self.update_list_b)
        self.list_b = QListWidget()
        self.list_b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.list_b.itemClicked.connect(self.handle_list_b_click)

        self.toggle_button = QPushButton("Afficher/masquer")
        self.toggle_button.clicked.connect(self.toggle_lists)

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.empty_widget)
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
        self.listen_button.setFixedHeight(40)
        self.listen_button.setFixedWidth(120)
        self.next_button = QPushButton(" > ")
        self.next_button.setFixedHeight(40)
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

        # Check if List A is visible.
        if self.list_a.isVisible():
            self.list_a.hide()
            self.list_b.hide()
            self.empty_widget.show()
        else:
            self.empty_widget.hide()
            self.list_a.show()
            self.list_b.show()

    def toggle_hide_next_button(self, state: bool):
        """Toggle the visibility of the next button.
        state : checkbox is checked or not ?"""
        if state:  # Checkbox checked.
            self.next_button.hide()
        else:  # Checkbox unchecked.
            self.next_button.show()

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
        # Word are shuffled so not always the same image at the same place.
        random.shuffle(pair)
        # Pick a random word as good response, which will be pronounced (audio).
        audio = random.choice(pair)
        # Store this in current item.
        self.current_item = CurrentItem(pair[0], pair[1], audio)
        # Set paths.
        audio_path = PathManager.get_sound_path(self.current_item.audio)
        image1_path = PathManager.get_image_path(self.current_item.word1)
        image2_path = PathManager.get_image_path(self.current_item.word2)

        # Update the image labels with the new images.
        self.image_label1.set_image(image1_path, 0, 0)
        self.image_label2.set_image(image2_path, 0, 0)
        self.resize_images()
        # Update the audio playback function of the "Listen" button.
        try:
            self.listen_button.clicked.disconnect()
        except RuntimeError:
            pass
        self.listen_button.clicked.connect(lambda: self.play_audio(audio_path))

        # Play the audio automatically if the "Automatic Listening" option is checked.
        if self.opt_auto_listen.checkbox.isChecked():
            self.play_audio(audio_path)

    def image_label1_clicked(self, event):
        """When Image1 is clicked."""
        self.event = event
        if self.current_item is not None:
            self.check_answer(self.current_item.word1)

    def image_label2_clicked(self, event):
        """When Image2 is clicked."""
        self.event = event
        if self.current_item is not None:
            self.check_answer(self.current_item.word2)

    def check_answer(self, selected_word):
        """Check if clicked image corresponds to audio."""

        # self.set_ui_state("disabled")

        if self.current_item is None:
            return None

        correct_word = self.current_item.audio

        if selected_word == correct_word:
            self.current_item.score += 1
            # FIXME
            if self.opt_success_sound.checkbox.isChecked():
                success_sound = self.get_random_success_sound()
                self.play_audio(success_sound)
                # Wait for the sound to finish.
                while self.current_sound.isPlaying():
                    QApplication.processEvents()
                    time.sleep(0.1)
            else:
                #QMessageBox.information(self, "Bravo!", f"La réponse est correcte: {correct_word}")
                pass
            # Go to next item.
            self.next_item()
        # If erroneous response.
        else:
            #QMessageBox.warning(self, "Erreur", f"La réponse est incorrecte. La bonne réponse est : {correct_word}")
            # Sound : "This is..."
            this_is_sound = PathManager.get_sound_path("_ça c'est")
            self.play_audio(this_is_sound)
            # Sound : the wrong word, which completes "This is...".
            wrong_word = selected_word
            wrong_sound = PathManager.get_sound_path(wrong_word)
            self.play_audio(wrong_sound)
            # Sound : "Show me..."
            show_me_sound = PathManager.get_sound_path("_montre moi")
            self.play_audio(show_me_sound)
            # Sound : the word we ask.
            correct_word_sound = PathManager.get_sound_path(correct_word)
            self.play_audio(correct_word_sound)

        self.current_item.total_attempts += 1
        # self.set_ui_state("enabled")

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

    def set_ui_state(self, state: str):
        """Enable or disable important parts of UI.
        Purpose : not having a child clicking 100 times on a button which produces 100 sounds."""

        widgets = [self.listen_button, self.next_button,
                   self.list_a, self.list_b,
                   self.image_label1, self.image_label2]

        if state == "enabled":
            for w in widgets:
                w.setEnabled(True)
                # w.blockSignals(False)  # Works bad.
            print("UI enabled")

        if state == "disabled":
            for w in widgets:
                w.setEnabled(False)
                # w.blockSignals(True)
            print("UI disabled")

    def play_audio(self, file: Path):
        """Play an audio file.
        WARNING : Add this line into the __init__ of the QMainWindow, else sound will be stopped
        when the function ends (so fast we won't hear anything).
            self.current_sound = None
        """
        self.set_ui_state("disabled")
        # Do nothing if sound is already playing.
        while self.current_sound.isPlaying():
            return
            # QApplication.processEvents()
            # time.sleep(0.1)

        print(f"Play {file}.")
        # Reinit sound an set source file.
        self.current_sound = QSoundEffect()
        self.current_sound.setSource(QUrl.fromLocalFile(file))
        # Start playing the sound.
        self.current_sound.setVolume(1)
        self.current_sound.play()

        # Wait for the sound to end.
        while self.current_sound.isPlaying():
            QApplication.processEvents()
            time.sleep(0.1)
        self.set_ui_state("enabled")

    def get_random_success_sound(self) -> Path:
        """Return a random success sound file from the 'success' sounds directory."""
        sounds_dir = importlib.resources.files("data") / "sounds" / "success"
        files = [f for f in sounds_dir.iterdir() if f.is_file() and f.suffix.lower() == ".wav"]
        # If no sound files in folder (should be impossible) FIXME.
        if not files == []:
            random_sound = random.choice(files)
            return random_sound

    def save_options_to_file(self):
        """Save the current options to the options file."""
        self.options_manager.set_option("random_order", self.opt_random.checkbox.isChecked())
        self.options_manager.set_option("auto_listen", self.opt_auto_listen.checkbox.isChecked())
        self.options_manager.set_option("success_sound", self.opt_success_sound.checkbox.isChecked())
        self.options_manager.save_options()

    def open_pdf(self, file_name):
        if platform.system() == "Windows":
            os.startfile(file_name)
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", file_name])
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", file_name])

    def show_about_dialog(self):
        """Display an About Dialog for the application."""

        license_info = """
            Ce programme est distribué gratuitement sans aucune garantie, sous licence <a
            href="https://creativecommons.org/licenses/by-nc-nd/4.0/deed.fr">Creative Commons CC
            BY-NC-ND.</a>
            <br><br>
            Les symboles pictographiques utilisés sont la propriété du
            Gouvernement d'Aragon et ont été créés par Sergio Palao pour ARASAAC
            (http://www.arasaac.org), qui les distribuent sous Licence
            <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr">Creative Commons CC
            BY-NC-SA.</a>.
            <br>
            Certains pictogrammes sont la propriété de Gautier Cailly et sont distribués sous
            la même licence que le programme.
            <br>
            L'icône du programme a été dessiné par <a href="https://www.flaticon.com/fr/icones-gratuites/chaussure">Freepik</a>.
            <br>
            Les sons sont sous licence Pixabay, ou CC0. Merci à Kevin Luce.
            """

        # Create an instance of the AboutDialog.
        about_dialog = AboutDialog(parent = self,
                                   app_name=SoftwareInfo.NAME,
                                   app_version=SoftwareInfo.VERSION,
                                   app_author=SoftwareInfo.AUTHOR,
                                   website=SoftwareInfo.WEBSITE,
                                   info = license_info)
        # Show the AboutDialog.
        about_dialog.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
