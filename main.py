"""catyhoo — a small, cross-platform pixel-art desktop cat (visual-only rewrite).

Run: python main.py
"""
import os
import sys

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from animation import MEDIA
from cat import CatWindow


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # live in the tray after hiding

    family = "Sans Serif"
    fid = QFontDatabase.addApplicationFont(os.path.join(MEDIA, "pixelmix.ttf"))
    fams = QFontDatabase.applicationFontFamilies(fid)
    if fams:
        family = fams[0]

    cat = CatWindow(family)  # noqa: F841 (kept alive by reference)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
