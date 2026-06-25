"""The help "book" window above the cat: a read-only text page."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QTextEdit

from animation import colorkey_pixmap


class BookWindow(QWidget):
    def __init__(self, bg_path, font_family):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        pix = colorkey_pixmap(bg_path)
        self.setFixedSize(pix.size())
        bg = QLabel(self)
        bg.setPixmap(pix)
        bg.setGeometry(0, 0, pix.width(), pix.height())

        # text sits inside the page rectangle (relx .1 / rely .1 / .81 x .82),
        # matching the legacy Workbook layout.
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.text.setFont(QFont(font_family, 11))
        self.text.setStyleSheet(
            "QTextEdit { background:#fcefe4; color:#100000; border:none; }"
        )
        self.text.setGeometry(
            int(pix.width() * 0.1), int(pix.height() * 0.1),
            int(pix.width() * 0.81), int(pix.height() * 0.82),
        )

    def append_text(self, text):
        self.text.append(f"\n{text}")
