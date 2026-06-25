"""The little command prompt next to the cat.

v1: an empty shell. The input box works, but there is no parser/command logic
yet (that's a stripped feature documented in FEATURES.md). On Enter it just
echoes the line into the book and clears.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit

from animation import colorkey_pixmap


class PromptWindow(QWidget):
    def __init__(self, bg_path, font_family, on_submit):
        super().__init__()
        self.on_submit = on_submit
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        pix = colorkey_pixmap(bg_path)
        self.setFixedSize(pix.size())
        bg = QLabel(self)
        bg.setPixmap(pix)
        bg.setGeometry(0, 0, pix.width(), pix.height())

        self.entry = QLineEdit(self)
        self.entry.setFont(QFont(font_family, 11))
        self.entry.setStyleSheet(
            "QLineEdit { background:#fff7f5; color:#100000; border:none; padding:2px; }"
        )
        ew, eh = int(pix.width() * 0.8), 28
        self.entry.setGeometry((pix.width() - ew) // 2, (pix.height() - eh) // 2, ew, eh)
        self.entry.returnPressed.connect(self._submit)

    def _submit(self):
        text = self.entry.text().strip()
        self.entry.clear()
        if text and self.on_submit:
            self.on_submit(text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
