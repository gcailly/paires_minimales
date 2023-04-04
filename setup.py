from cx_Freeze import setup, Executable

# Remplacez "mon_script" par le nom de votre fichier de script sans l'extension .py
executables = [Executable("src/main.py")]

options = {
    "build_exe": {
        "excludes": [
            "tkinter",
            "unittest",
            "email",
            "http",
            "xml",
            "pydoc",
            "PySide6.QtNetwork",
        ],
        "zip_include_packages": ["PySide6"],
    },
}

setup(
    name="Les Paires Minimales",
    version="1.0.0",
    description="",
    options=options,
    executables=executables
)
