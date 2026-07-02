"""The little command prompt next to the cat.

v1: an empty shell. The input box works, but there is no parser/command logic
yet (that's a stripped feature documented in FEATURES.md). On Enter it just
echoes the line into the book and clears.
"""
from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit

_HISTORY_LIMIT = 100

from animation import colorkey_pixmap


class PromptWindow(QWidget):
    def __init__(self, bg_path, font_family, on_submit):
        super().__init__()
        self.on_submit = on_submit
        self._history: list[str] = []   # oldest first
        self._hist_idx: int = -1        # -1 = not browsing
        self._hist_draft: str = ""      # saved draft while browsing
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
        self.entry.installEventFilter(self)  # intercept Up/Down/Escape before QLineEdit does

    def _submit(self):
        text = self.entry.text().strip()
        self.entry.clear()
        self._hist_idx = -1
        self._hist_draft = ""
        if text:
            # dedup: don't add if identical to the last entry
            if not self._history or self._history[-1] != text:
                self._history.append(text)
                if len(self._history) > _HISTORY_LIMIT:
                    self._history.pop(0)
            if self.on_submit:
                self.on_submit(text)

    def set_font_family(self, font_family):
        self.entry.setFont(QFont(font_family, 11))

    def eventFilter(self, obj, event):
        """Intercept key presses on the entry before QLineEdit handles them."""
        if obj is self.entry and event.type() == QEvent.KeyPress:
            key = event.key()
            if key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Escape):
                self.keyPressEvent(event)
                return True  # consumed
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up:
            if self._history:
                if self._hist_idx == -1:
                    # save current draft before entering history
                    self._hist_draft = self.entry.text()
                    self._hist_idx = len(self._history) - 1
                elif self._hist_idx > 0:
                    self._hist_idx -= 1
                self.entry.setText(self._history[self._hist_idx])
                self.entry.end(False)   # move cursor to end
        elif key == Qt.Key_Down:
            if self._hist_idx != -1:
                if self._hist_idx < len(self._history) - 1:
                    self._hist_idx += 1
                    self.entry.setText(self._history[self._hist_idx])
                else:
                    self._hist_idx = -1
                    self.entry.setText(self._hist_draft)
                self.entry.end(False)
        elif key == Qt.Key_Escape:
            if self.entry.text():
                self.entry.clear()
                self._hist_idx = -1
                self._hist_draft = ""
            else:
                self.hide()
        else:
            super().keyPressEvent(event)
