import os
from cx_Freeze import setup, Executable

os.environ["TCL_LIBRARY"] = r'C:\Python310\tcl\tcl8.6'
os.environ["TK_LIBRARY"] = r'C:\Python310\tcl\tk8.6'

base = None

executables = [Executable("main.py", base=base)]

packages = ["darkdetect", "os", "ssl", "PySimpleGUI", "PySimpleGUIWx", "pytube"]
options = {
    'build_exe': {
        'packages': packages,
    },
}

setup(
    name="PySimpleGUI",
    options=options,
    version="1.0",
    description='A simple youtube resource downloader',
    author="Tsaitou7361",
    executables=executables
)
