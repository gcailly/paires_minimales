"""
python src\setup.py build
"""

import sys
import importlib.resources
from cx_Freeze import setup, Executable

from main import SoftwareInfo


base = None
if sys.platform == "win32":
    base = "Win32GUI"


# Remplacez "mon_script" par le nom de votre fichier de script sans l'extension .py
executables = [Executable("src/main.py",
                          base=base,
                          icon=importlib.resources.files("data") / "app_icon.ico",
                          target_name="lpm.exe")]


options = {
    "build_exe": {
        "includes": ["data"],
        "zip_include_packages": ["PySide6"],
        "excludes": [
            "tkinter",
            "unittest",
            "email",
            "http",
            "xml",
            "pydoc"]
    },
}


setup(
    name=SoftwareInfo.NAME,
    version=SoftwareInfo.VERSION,
    description="",
    options=options,
    executables=executables
)
