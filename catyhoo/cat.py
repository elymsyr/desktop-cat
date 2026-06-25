"""CatWindow: the animated cat. State machine ported verbatim from the legacy
tkinter app, with window.after -> QTimer.singleShot and absolute screen coords
replaced by the primary screen's available geometry (so it works on any
resolution / OS, and sits above the real taskbar/panel)."""
import os
from random import choice

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QSystemTrayIcon, QMenu

from animation import EVENTS, CAT_SIZE, MEDIA, load_frames
from prompt import PromptWindow
from book import BookWindow

INTRO = ("Right-click the cat to toggle the prompt & book.\n"
         "Drag to move. Double-click to hide to the tray.\n"
         "This is the visual-only rewrite (catyhoo).")


class CatWindow(QWidget):
    def __init__(self, font_family):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(CAT_SIZE, CAT_SIZE)

        self.images, self.imageGif = load_frames()
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, CAT_SIZE, CAT_SIZE)

        # screen-relative bounds (replace legacy hardcoded 1400/922/500/1700)
        geo = QGuiApplication.primaryScreen().availableGeometry()
        self.left = geo.left()
        self.right_x = geo.right() - CAT_SIZE            # max cat x
        self.floor_y = geo.bottom() - CAT_SIZE           # legacy INITIAL_Y
        self.top_y = geo.top()
        w = geo.width()
        self.near_left = self.left + 0.26 * w            # legacy x < 500
        self.near_right = self.left + 0.885 * w          # legacy x > 1700
        self.center_lo = self.left + 0.47 * w            # legacy INITIAL_X-500
        self.center_hi = self.left + 0.78 * w            # legacy INITIAL_X+100

        # state
        self.animation_running = True
        self.falling = False
        self.long_sleep = False
        self.prompt_vis = True
        self.book_vis = True
        self.x = int(self.right_x * 0.73)
        self.y = self.floor_y
        self.cycle = 0
        self.current_event_cycle = choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18])
        self.current_event_cycle_index = 0
        self.event_number = EVENTS[self.current_event_cycle][0][0]

        # companion windows + tray
        self.prompt = PromptWindow(os.path.join(MEDIA, "messagebox.png"),
                                   font_family, self.book_append)
        self.book = BookWindow(os.path.join(MEDIA, "books", "book_main.png"), font_family)
        self.book.append_text(INTRO)
        self._make_tray()

        self.move(self.x, self.y)
        self.prompt.show()
        self.book.show()
        self.show()
        self._reposition()
        QTimer.singleShot(1, self.update_frame)

    # ---- tray --------------------------------------------------------------
    def _make_tray(self):
        self.tray = QSystemTrayIcon(QIcon(os.path.join(MEDIA, "tray-icon.png")), self)
        menu = QMenu()
        menu.addAction("Show", self.show_all)
        menu.addAction("Exit", QGuiApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda r: self.show_all() if r == QSystemTrayIcon.Trigger else None)
        self.tray.show()

    def book_append(self, text):
        self.book.append_text(text)

    # ---- show / hide -------------------------------------------------------
    def show_all(self):
        self.show()
        if self.prompt_vis:
            self.prompt.show()
        if self.book_vis:
            self.book.show()
        self._reposition()

    def hide_all(self):
        self.hide()
        self.prompt.hide()
        self.book.hide()

    def toggle_companions(self):
        self.prompt_vis = self.book_vis = not (self.prompt_vis and self.book_vis)
        self.prompt.setVisible(self.prompt_vis)
        self.book.setVisible(self.book_vis)
        if self.prompt_vis:
            self._reposition()

    def _reposition(self):
        self.prompt.move(self.x - 295, self.y - 110)
        self.book.move(self.x - 304, self.y - 585)

    # ---- drag --------------------------------------------------------------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_off = e.globalPosition().toPoint() - self.pos()
        elif e.button() == Qt.RightButton:
            self.toggle_companions()

    def mouseMoveEvent(self, e):
        if not (e.buttons() & Qt.LeftButton):
            return
        self.animation_running = False
        p = e.globalPosition().toPoint() - self._drag_off
        self.x = max(min(p.x(), self.right_x), self.left)
        self.y = max(min(p.y(), self.floor_y), self.top_y)
        self.move(self.x, self.y)
        self._reposition()

    def mouseReleaseEvent(self, e):
        if not self.animation_running:
            self.animation_running = True
            QTimer.singleShot(100, self.update_frame)

    def mouseDoubleClickEvent(self, e):
        self.hide_all()

    # ---- animation state machine (ported) ----------------------------------
    def reset_cycle(self, events=(0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18), event_cycle=True):
        if event_cycle:
            self.current_event_cycle = choice(events)
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def gif_work(self):
        if self.cycle < len(self.imageGif[self.images[self.event_number]]) - 1:
            self.cycle += 1
        else:
            self.cycle = 0
            self.event_number = self.choose_event_change()

    def update_frame(self):
        if not self.animation_running:
            return

        if self.y + 40 < self.floor_y:
            if not self.falling:
                self.falling = True
                self.long_sleep = False
                self.reset_cycle([21])
            self.y += 40 if abs(self.y - self.floor_y) >= 40 else abs(self.y - self.floor_y)
        elif self.y < self.floor_y:
            self.falling = True
            self.y += 40 if abs(self.y - self.floor_y) >= 40 else abs(self.y - self.floor_y)
        elif abs(self.y - self.floor_y) <= 20 and self.falling:
            if self.prompt_vis:
                self.reset_cycle([22, 23, 24])
            else:
                self.current_event_cycle = choice([7, 14, 15, 0, 8, 1, 9, 5, 13, 6, 16, 17, 18])
            self.reset_cycle(event_cycle=False)
            self.falling = False
            self.y = self.floor_y

        frame = self.imageGif[self.images[self.event_number]][self.cycle]
        if self.event_number in (8, 9, 3):
            self.x -= 6
        elif self.event_number in (18, 19, 13):
            self.x += 6

        self.gif_work()
        self.move(self.x, self.y)
        self.label.setPixmap(frame)
        self._reposition()
        QTimer.singleShot(1, self.next_tick)

    def next_tick(self):
        n = self.event_number
        if n in (1, 2, 4, 5) or n - 10 in (1, 2, 4, 5):
            delay = 200
        elif n in (8, 9, 0) or n - 10 in (8, 9, 0):
            delay = 150
        elif n in (6, 16):
            delay = 1000
        elif n in (3, 13):
            delay = 160
        elif n in (7, 17):
            delay = 160
        elif n == 20:
            delay = 120
        else:
            delay = 150  # ponytail: legacy left these unscheduled; all reachable n are covered above
        QTimer.singleShot(delay, self.update_frame)

    def choose_event_change(self):
        if self.current_event_cycle_index < len(EVENTS[self.current_event_cycle][0]) - 1:
            self.current_event_cycle_index += 1
        elif self.long_sleep:
            self.current_event_cycle = 25
            self.current_event_cycle_index = 0
        elif self.x < self.near_left:
            self.current_event_cycle = choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18, 10, 11])
            self.current_event_cycle_index = 0
        elif self.x > self.near_right:
            self.current_event_cycle = choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18, 2, 3])
            self.current_event_cycle_index = 0
        else:
            nxt = choice(EVENTS[self.current_event_cycle][1])
            while (self.x < self.center_lo or self.x > self.center_hi) and nxt == 19:
                nxt = choice(EVENTS[self.current_event_cycle][1])
            self.current_event_cycle = nxt
            self.current_event_cycle_index = 0
        return EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]
