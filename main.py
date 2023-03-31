import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QWidget, QMenu, QMenuBar, QPushButton, QGroupBox,
                                QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QListWidget, QHBoxLayout)
from PySide6.QtCore import Qt

class SoftwareInfo:
    NAME = "Les Paires Minimales"
    VERSION = "1.0.0"
    AUTHOR = "Gautier Cailly"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{SoftwareInfo.NAME} {SoftwareInfo.VERSION}")

        # Création du menu
        self.create_menu()

        # Création du layout principal
        main_layout = QGridLayout()

        # Création des listes verticales
        list_widget_1 = QListWidget()
        list_widget_2 = QListWidget()

        # Ajout d'éléments de démonstration
        for i in range(10):
            list_widget_1.addItem(f"Élément {i + 1}")
            list_widget_2.addItem(f"Élément {i + 11}")

        # Création d'un QHBoxLayout pour les deux listes
        lists_layout = QHBoxLayout()
        lists_layout.addWidget(list_widget_1)
        lists_layout.addWidget(list_widget_2)

        main_layout.addLayout(lists_layout, 0, 0)

        # Création de la grille avec une colonne et deux lignes
        buttons_layout = QGridLayout()

        # Ajout des boutons dans la grille
        button_images = QPushButton("Images")
        button_listen = QPushButton("Écouter")

        buttons_layout.addWidget(button_images, 0, 0)
        buttons_layout.addWidget(button_listen, 1, 0)

        main_layout.addLayout(buttons_layout, 0, 1)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        main_layout.setColumnMinimumWidth(0, 200)  # Fixe la largeur de la colonne des listes à 200 px

    def create_menu(self):
        menu_bar = QMenuBar(self)

        help_menu = QMenu("Aide", self)
        menu_bar.addMenu(help_menu)

        about_action = menu_bar.addAction("A propos")
        about_action.triggered.connect(self.show_about_dialog)

        self.setMenuBar(menu_bar)

    def show_about_dialog(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("A propos")
        about_dialog.setMinimumWidth(400)  # Fixe la largeur minimale de la fenêtre à 400 pixels
        # Empêcher la redimension du QDialog
        about_dialog.setFixedSize(self.size())        # Création du layout et des widgets
        layout = QVBoxLayout()

        software_name = QLabel(f"<b>{SoftwareInfo.NAME}</b>")
        version = QLabel(f"Version: {SoftwareInfo.VERSION}")
        author = QLabel(f"Auteur: {SoftwareInfo.AUTHOR}")
        website = QLabel('<a href="https://www.oortho.fr">www.oortho.fr</a>')
        credits = QLabel("Crédits images: ARASAAC")
        paragraph = QLabel("Ceci est un paragraphe de texte lambda. Il sert à décrire des informations supplémentaires sur l'application ou à fournir des instructions aux utilisateurs.")

        paragraph.setWordWrap(True)
        # paragraph.setMaximumWidth(500)

        # Ajout des widgets au layout
        layout.addWidget(software_name)
        layout.addWidget(version)
        layout.addWidget(author)
        layout.addWidget(website)
        layout.addWidget(credits)
        layout.addWidget(paragraph)

        # Création des boutons d'action
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(about_dialog.accept)
        layout.addWidget(button_box)

        about_dialog.setLayout(layout)

        # Affichage de la fenêtre modale
        about_dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
