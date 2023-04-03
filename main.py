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
    Définit les informations générales du logiciel, y compris le nom, la version, l'auteur et le
    site web associé.
    """
    NAME = "Les Paires Minimales"
    VERSION = "1.0.0"
    AUTHOR = "Gautier Cailly"
    WEBSITE = "www.oortho.fr"




class PathManager:
    """
    Cette classe fournit des méthodes statiques pour obtenir les chemins d'accès aux fichiers
    image et son correspondant à un mot donné.
    """

    @staticmethod
    def get_image_path(word: str) -> Path:
        """Obtient le chemin d'accès au fichier image correspondant au mot donné."""
        with importlib.resources.path("data.images", f"{word}.png") as image_path:
            return image_path

    @staticmethod
    def get_sound_path(word: str) -> Path:
        """Obtient le chemin d'accès au fichier son correspondant au mot donné."""
        with importlib.resources.path("data.sounds", f"{word}.wav") as sound_path:
            return sound_path



class AboutDialog(QDialog):
    """
    Crée et affiche une fenêtre à propos avec des informations sur le logiciel, l'auteur et les
    crédits d'image.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur de la boîte de dialogue."""

        self.setWindowTitle("A propos")
        self.setMinimumWidth(300)
        layout = QVBoxLayout()

        # Création du contenu.
        content_text = f"""
            <b>{SoftwareInfo.NAME}
            </b><br>
            Version: {SoftwareInfo.VERSION}
            <br>
            Auteur: {SoftwareInfo.AUTHOR}
            <br>
            <a href="https://www.oortho.fr">www.oortho.fr</a><br> <br>
            Crédits images: ARASAAC, Gautier Cailly
            <br>
            <br>
            Ceci est un paragraphe de texte lambda.
            Il sert à décrire des informations supplémentaires sur l'application ou à fournir des
            instructions aux utilisateurs.
            """
        content = QLabel(content_text)
        content.setWordWrap(True)
        layout.addWidget(content)

        # Création des boutons d'action.
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def show(self):
        """Affiche la boîte de dialogue modale."""
        self.exec()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{SoftwareInfo.NAME} {SoftwareInfo.VERSION}")
        self.create_menu()
        self.init_ui()


    def create_menu(self):
        """Crée le menu."""

        menu_bar = QMenuBar(self)

        help_menu = QMenu("Aide", self)
        menu_bar.addMenu(help_menu)

        about_action = menu_bar.addAction("A propos")
        about_action.triggered.connect(self.show_about_dialog)

        self.setMenuBar(menu_bar)


    def init_ui(self):

        # Créer le layout principal
        main_layout = QHBoxLayout()

        # Créer les listes A et B
        self.list_a = QListWidget()
        self.list_b = QListWidget()
        self.list_a.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.list_b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Widget de même largeur que les listes pour les remplacer quand elles sont masquées.
        self.empty_widget = QWidget()
        self.empty_widget.setFixedWidth(200)

        # Créer le bouton pour masquer/montrer les listes
        self.toggle_button = QPushButton("Masquer/Montrer")
        self.toggle_button.clicked.connect(self.toggle_lists)
        # self.toggle_button.setFixedSize(100, 30)  # Définir une taille fixe pour le bouton

        # Créer un QVBoxLayout pour les listes et le bouton
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.list_a)
        self.left_layout.addWidget(self.list_b)
        self.left_layout.addWidget(self.toggle_button)
        lists_width = self.list_a.sizeHint().width()
        self.toggle_button.setFixedWidth(lists_width)

        # Créer les deux images côte à côte
        self.image_label1 = QLabel()
        self.image_label2 = QLabel()
        self.pixmap1 = QPixmap("image1.png")
        self.pixmap2 = QPixmap("image2.png")
        self.image_label1.setPixmap(self.pixmap1)
        self.image_label2.setPixmap(self.pixmap2)
        self.image_label1.setAlignment(Qt.AlignCenter)
        self.image_label2.setAlignment(Qt.AlignCenter)

        # Créer un QHBoxLayout pour les images
        images_layout = QHBoxLayout()
        images_layout.addWidget(self.image_label1)
        images_layout.addWidget(self.image_label2)

        # Créer le bouton "Écouter"
        self.listen_button = QPushButton("Écouter")
        self.listen_button.setFixedHeight(24)
        
        # Créer un QHBoxLayout pour centrer le bouton "Écouter"
        listen_button_layout = QHBoxLayout()
        listen_button_layout.addWidget(self.listen_button)
        listen_button_layout.setAlignment(self.listen_button, Qt.AlignCenter)

        # Ajouter les images et le bouton à un QVBoxLayout
        right_layout = QVBoxLayout()
        right_layout.addLayout(images_layout)  # Ajouter le QHBoxLayout des images ici
        right_layout.addLayout(listen_button_layout)  # Ajouter le QHBoxLayout du bouton "Écouter"

        # Ajouter les layouts de gauche et de droite au layout principal
        main_layout.addLayout(self.left_layout)
        main_layout.addLayout(right_layout)

        # Largeur fixe des listes et du bouton.
        fixed_width = 200
        self.list_a.setFixedWidth(fixed_width)
        self.list_b.setFixedWidth(fixed_width)
        self.toggle_button.setFixedWidth(fixed_width)

        # Créer un widget central et définir le layout principal
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        # Get the screen size
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()

        # Calculate the desired size as 80% of the screen's width and height
        desired_width = int(screen_size.width() * 0.8)
        desired_height = int(screen_size.height() * 0.8)

        # Set the size of the main window
        self.resize(desired_width, desired_height)

        # self.showMaximized()
        self.resize_images()
        

    def resize_images(self):

        # Largeur et hauteur disponibles pour les images
        available_width = self.width() - self.list_a.width()

        # Hauteur de la fenêtre principale - hauteur du bouton "Écouter" - marges
        available_height = self.height() - self.listen_button.height() - self.layout().contentsMargins().top() - self.layout().contentsMargins().bottom()
        print(f"""
            available_height : {available_height}
            self.height() : {self.height()}
            self.toggle_button.height() : {self.listen_button.height()}
            self.layout().contentsMargins().top() : {self.layout().contentsMargins().top()}
            self.layout().contentsMargins().bottom() : {self.layout().contentsMargins().bottom()}
        """)


        width = int(available_width * 0.6)  # Utilisez 60% de la largeur disponible pour chaque image
        height = int(available_height * 0.6)  # Utilisez 60% de la hauteur disponible pour les images

        # Redimensionnez les images en fonction de la taille de la fenêtre
        self.image_label1.setPixmap(self.pixmap1.scaled(width, height, Qt.KeepAspectRatio))
        self.image_label2.setPixmap(self.pixmap2.scaled(width, height, Qt.KeepAspectRatio))


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_images()


    def toggle_lists(self):
        if self.list_a.isVisible():
            left_layout_index = self.left_layout.indexOf(self.list_a)
            self.left_layout.removeWidget(self.list_a)
            self.left_layout.removeWidget(self.list_b)
            self.list_a.hide()
            self.list_b.hide()

            self.left_layout.insertWidget(left_layout_index, self.empty_widget)
            self.empty_widget.show()
        else:
            left_layout_index = self.left_layout.indexOf(self.empty_widget)
            self.left_layout.removeWidget(self.empty_widget)
            self.empty_widget.hide()

            self.left_layout.insertWidget(left_layout_index, self.list_a)
            self.left_layout.insertWidget(left_layout_index + 1, self.list_b)
            self.list_a.show()
            self.list_b.show()

    def show_about_dialog(self):
        """Affiche une boîte de dialogue d'informations sur l'application."""
        about_dialog = AboutDialog()
        about_dialog.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
