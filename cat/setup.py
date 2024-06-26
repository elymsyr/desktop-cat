from distutils.core import setup
import py2exe
import sys
import os

# Ensure 'py2exe' argument is passed to avoid running setup.py without py2exe command
sys.argv.append('py2exe')

# Function to gather data files
def find_data_files(source, target, patterns):
    data_files = []
    for root, _, files in os.walk(source):
        for filename in files:
            if any(filename.endswith(pattern) for pattern in patterns):
                file_path = os.path.join(root, filename)
                target_path = os.path.join(target, os.path.relpath(root, source))
                data_files.append((os.path.dirname(target_path), [file_path]))
    return data_files

# Define data files
data_files = []
data_files += find_data_files('media', 'media', ['.png', '.ttf'])
data_files += find_data_files('media/books', 'media/books', ['.png'])
data_files += find_data_files('media/gifs', 'media/gifs', ['.gif'])
data_files += find_data_files('media/gifs_others', 'media/gifs_others', ['.gif'])
data_files += find_data_files('data', 'data', ['.json'])

setup(
    zipfile = None,
    windows = [{
            "script":"desktop_cat.py",
            "icon_resources": [(1, "media/tray-icon.ico")],
            "dest_base":"Dektop Cat",
            "version": "demo",
            "description": "This is a test version. Many functionalities are not activeted yet."
            }],
    options={
        'py2exe': {
            'bundle_files': 1,
            'compressed': True,
            'includes': [
                'tkinter',
                "PIL",
                "PIL.Image",
                "PIL.ImageTk",
                'random',
                'webbrowser',
                'traceback',
                'pyglet',
                'workload',
                'time',
                'pystray',
                'pygetwindow',
                'sqlite3',
                'subprocess',
                'shutil',
                'urllib',
                'json',
                'multiprocessing',
            ],  # Ensure all necessary modules are included
        }
    },
    data_files=data_files,  # Include data files
    packages=[]
)
