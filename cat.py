"""CatWindow: the animated cat. State machine ported verbatim from the legacy
tkinter app, with window.after -> QTimer.singleShot and absolute screen coords
replaced by the primary screen's available geometry (so it works on any
resolution / OS, and sits above the real taskbar/panel)."""
import os
from random import choice

from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QGuiApplication, QIcon, QImage, QRegion
from PySide6.QtWidgets import QWidget, QLabel, QSystemTrayIcon, QMenu

from animation import EVENTS, CAT_SIZE, MEDIA, load_frames
from prompt import PromptWindow
from book import BookWindow
import config
import commands
import mcp_server
import providers
import tools

INTRO = ("Right-click the cat to toggle the prompt & book.\n"
         "Drag to move. Double-click to hide to the tray.\n"
         "This is the visual-only rewrite (catyhoo).")

# Surface detection (cat lands on flat horizontal edges while falling).
# These are calibration knobs against real pixels — tune if behavior is off.
LOOKAHEAD = 200          # ponytail: max px scanned below the paws (covers a probe gap)
VDIFF = 22               # per-pixel luminance step that counts as an edge
CONT_FRAC = 0.8          # share of sampled columns that must form a continuous edge
FLAT_RANGE = 35          # max luminance spread along the row -> "horizontally flat"
FOOT_BAND = (30, 130)    # column range scanned: wide enough that the cat's
#                          transparent side margins give clear columns even while
#                          it rests on a line (the line sits at the masked paw row
#                          in the centre)
OVERLAP = 16             # px the strip starts above the paws (keeps a resting line inside it)
STICK_TOL = 12           # slack before a resting cat decides its ground is gone
PROBE_MS = 150           # how often the surface probe runs (off the animation path)
MISS_LIMIT = 8           # consecutive empty probes before the cat lets go (debounce ~1.2s)


def _opaque_bounds(pixmap, thresh=10):
    """Bounding box (minx, miny, maxx, maxy) of the non-transparent pixels in a
    frame. Used to shrink the cat's clickable/draggable area to its body — and to
    keep the empty space below the paws untouchable."""
    img = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
    w, h, st = img.width(), img.height(), img.bytesPerLine()
    a = bytes(img.constBits())
    row_has = lambda y: any(a[y * st + x * 4 + 3] > thresh for x in range(w))
    col_has = lambda x: any(a[y * st + x * 4 + 3] > thresh for y in range(h))
    miny = next((y for y in range(h) if row_has(y)), 0)
    maxy = next((y for y in range(h - 1, -1, -1) if row_has(y)), h - 1)
    minx = next((x for x in range(w) if col_has(x)), 0)
    maxx = next((x for x in range(w - 1, -1, -1) if col_has(x)), w - 1)
    return minx, miny, maxx, maxy


def _lowest_opaque_row(pixmap):
    """Row of the lowest non-transparent pixel in a frame = where the paws are.
    The cat sprite leaves empty space below the paws inside the 160px frame, so
    this is what we align to a surface (not the window bottom)."""
    img = pixmap.toImage()
    w, h = img.width(), img.height()
    for y in range(h - 1, -1, -1):
        for x in range(w):
            if img.pixelColor(x, y).alpha() > 10:
                return y
    return h - 1


def _flat_line(buf, stride, height, cols, masks, vdiff, cont_frac, flat_range):
    """Topmost row r in [1, height) that is a genuine flat horizontal line: a
    near-continuous vertical edge AND horizontally uniform along the row. The
    uniformity check rejects text/icons (non-uniform rows); the continuity check
    rejects short shape edges. `masks[c]` is the strip row of the cat's own lowest
    opaque pixel in column c; only rows strictly below it (in both r and r-1) are
    considered for that column, so the cat never detects itself. `buf` is a
    grayscale-8 buffer. Returns r, or None."""
    min_cols = max(4, len(cols) // 4)
    for r in range(1, height):
        base, prev = r * stride, (r - 1) * stride
        hits = 0
        rmin, rmax = 255, 0
        usable = 0
        for c in cols:
            if r - 1 <= masks[c]:      # row (or the one above) is the cat itself
                continue
            usable += 1
            v = buf[base + c]
            if abs(v - buf[prev + c]) > vdiff:
                hits += 1
            if v < rmin:
                rmin = v
            if v > rmax:
                rmax = v
        if usable >= min_cols and hits >= usable * cont_frac and (rmax - rmin) <= flat_range:
            return r
    return None


class CatWindow(QWidget):
    def __init__(self, font_family):
        super().__init__()
        config.load()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
                            | Qt.X11BypassWindowManagerHint)  # let cat cover panel/taskbar area
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(CAT_SIZE, CAT_SIZE)

        self.images, self.imageGif = load_frames()
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, CAT_SIZE, CAT_SIZE)

        # where the visible paws sit inside the 160px frame (lowest opaque row of
        # an idle frame) — so the cat rests *on* a surface, not floating above it.
        # ponytail: one-time per-pixel scan of a single frame; this is the knob.
        self.paw_row = _lowest_opaque_row(self.imageGif[self.images[1]][0])

        # Restrict where the cat can be grabbed/clicked to its body. Mask the
        # window to the union bounding box of the sprites (first frame of each
        # gif) with a small margin — the empty space below the paws and the side
        # margins become click-through, never grabbing the cat.
        # ponytail: one-time scan of ~21 frames; mask rendering is unchanged since
        # the box contains every opaque pixel.
        minx, miny, maxx, maxy = CAT_SIZE, CAT_SIZE, 0, 0
        for name in self.images:
            bx0, by0, bx1, by1 = _opaque_bounds(self.imageGif[name][0])
            minx, miny, maxx, maxy = min(minx, bx0), min(miny, by0), max(maxx, bx1), max(maxy, by1)
        m = 4  # margin to cover minor inter-frame leg/tail movement
        minx, miny = max(0, minx - m), max(0, miny - m)
        maxx, maxy = min(CAT_SIZE - 1, maxx + m), min(CAT_SIZE - 1, maxy + 1)
        self.setMask(QRegion(QRect(minx, miny, maxx - minx + 1, maxy - miny + 1)))

        # screen-relative bounds (replace legacy hardcoded 1400/922/500/1700)
        geo = QGuiApplication.primaryScreen().geometry()  # full screen, not taskbar-excluded
        self.left = geo.left()
        self.right_x = geo.right() - CAT_SIZE            # max cat x
        self.floor_y = geo.bottom() - self.paw_row       # paws on the screen edge
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
        self.ground_y = self.floor_y   # maintained by the probe timer, read by update_frame
        self._misses = 0
        self._mask_cache = {}          # id(frame pixmap) -> per-column cat-bottom strip row
        self.cycle = 0
        self.current_event_cycle = choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18])
        self.current_event_cycle_index = 0
        self.event_number = EVENTS[self.current_event_cycle][0][0]
        self._cur_frame = self.imageGif[self.images[self.event_number]][0]  # displayed pixmap

        # companion windows + tray
        self.prompt = PromptWindow(os.path.join(MEDIA, "messagebox.png"),
                                   font_family, self._on_submit)
        self.book = BookWindow(os.path.join(MEDIA, "books", "book_main.png"), font_family)
        self.book.append_text(INTRO)
        self._make_tray()
        tools.arm_reminders(self)  # re-arm reminders persisted from a previous run
        mcp_server.start(self)  # serves notify/time_event/reminder over MCP on a bg thread
        providers.start_receiver()  # listens for the Chrome extension's tab pushes

        # one reusable single-shot timer drives the loop. Restarting the *same*
        # timer cancels any pending fire, so a fast drag can never stack a second
        # animation chain (the old singleShot-per-tick approach could).
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.update_frame)

        # surface detection runs on its own slow timer (not the animation path),
        # so the grab cost never stutters the animation and checks happen at a
        # fixed interval. It maintains self.ground_y.
        self.probe_timer = QTimer(self)
        self.probe_timer.timeout.connect(self._probe)
        self.probe_timer.start(PROBE_MS)

        self.move(self.x, self.y)
        self.prompt.show()
        self.book.show()
        self.show()
        self._reposition()
        self.timer.start(1)

    # ---- tray --------------------------------------------------------------
    def _make_tray(self):
        self.tray = QSystemTrayIcon(QIcon(os.path.join(MEDIA, "tray-icon.png")), self)
        menu = QMenu()
        self.show_action = menu.addAction("Show")
        self.show_action.setCheckable(True)
        self.show_action.setChecked(True)
        self.show_action.toggled.connect(
            lambda on: self.show_all() if on else self.hide_all())
        menu.addAction("Exit", QGuiApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def book_append(self, text):
        self.book.append_text(text)

    def _on_submit(self, text):
        out = commands.dispatch(text, self)
        if out:
            self.book.append_text(out)

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
        self.timer.stop()
        p = e.globalPosition().toPoint() - self._drag_off
        self.x = max(min(p.x(), self.right_x), self.left)
        self.y = max(min(p.y(), self.floor_y), self.top_y)
        self.move(self.x, self.y)
        self._reposition()

    def mouseReleaseEvent(self, e):
        if not self.animation_running:
            self.animation_running = True
            self.timer.start(100)


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

        # Ground is maintained off-thread by the probe timer (no grab here).
        ground_y = self.ground_y

        if self.y + 40 < ground_y:
            if not self.falling:
                self.falling = True
                self.long_sleep = False
                self.reset_cycle([21])
            self.y += 40
        elif self.y < ground_y:
            self.falling = True
            self.long_sleep = False
            self.y = ground_y
        elif self.falling and abs(self.y - ground_y) <= 20:
            if self.prompt_vis:
                self.reset_cycle([22, 23, 24])
            else:
                self.current_event_cycle = choice([7, 14, 15, 0, 8, 1, 9, 5, 13, 6, 16, 17, 18])
            self.reset_cycle(event_cycle=False)
            self.falling = False
            self.y = ground_y
        elif (not self.falling) and ground_y - self.y > STICK_TOL:
            # the surface we were standing on vanished (window moved / walked off
            # its edge) -> start falling again toward the next ground.
            self.falling = True
            self.long_sleep = False
            self.reset_cycle([21])

        frame = self.imageGif[self.images[self.event_number]][self.cycle]
        if self.event_number in (8, 9, 3):
            self.x -= 6
        elif self.event_number in (18, 19, 13):
            self.x += 6

        self.gif_work()
        self.move(self.x, self.y)
        self._cur_frame = frame
        self.label.setPixmap(frame)
        self._reposition()
        self.next_tick()

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
        self.timer.start(delay)

    def choose_event_change(self):
        if self.falling:                      # falling overrides x-bias and long_sleep
            self.current_event_cycle = 21
            self.current_event_cycle_index = 0
            return EVENTS[21][0][0]
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

    # ---- surface detection (own timer, off the animation path) --------------
    def _probe(self):
        """Maintain self.ground_y. On/near the floor: it's just the floor (no
        grab). Otherwise probe for a flat line; debounce empty results so a
        momentary miss doesn't drop the cat off a surface it's resting on."""
        if not self.falling and self.y >= self.floor_y - STICK_TOL:
            self.ground_y = self.floor_y
            self._misses = 0
            return
        surf = self.detect_ground()
        if surf is None:
            self._misses += 1
            if self._misses >= MISS_LIMIT:
                self.ground_y = self.floor_y
        else:
            self._misses = 0
            self.ground_y = min(surf - self.paw_row, self.floor_y)

    def _frame_masks(self, cols, off):
        """Per-column strip row of the cat's own lowest opaque pixel in the
        currently-displayed frame (so the probe can ignore the cat itself).
        grabWindow captures our window too, and some frames have a flat bottom
        edge that would otherwise read as a phantom surface. Memoized per frame."""
        frame = self._cur_frame
        masks = self._mask_cache.get(id(frame))
        if masks is None:
            # ARGB32 little-endian -> alpha is byte 3 of each pixel. Reading raw
            # bytes is ~100x faster than pixelColor (which starved the loop).
            fimg = frame.toImage().convertToFormat(QImage.Format_ARGB32)
            fh, fstride = fimg.height(), fimg.bytesPerLine()
            fbuf = memoryview(fimg.constBits()).cast("B")
            masks = {}
            for c in cols:
                lo = -1
                base = c * 4 + 3
                for yy in range(fh - 1, -1, -1):
                    if fbuf[yy * fstride + base] > 10:
                        lo = yy
                        break
                masks[c] = lo - off   # cat-bottom in strip coords (negative if column empty)
            self._mask_cache[id(frame)] = masks
        return masks

    def detect_ground(self):
        """Grab a short strip below the paws and return the screen y of the
        topmost genuinely-flat horizontal line, or None. Columns where the cat's
        own sprite sits are masked out (see _frame_masks).
        # ponytail: Qt grabWindow -> grayscale -> sampled pure-Python scan; cheap
        # (short strip, central band, runs only on the PROBE_MS timer).
        # ponytail: assumes devicePixelRatio == 1; handle HiDPI only if needed.
        # On Wayland grabWindow yields a blank/uniform image -> no flat line ->
        # None, so it degrades to plain falling instead of a phantom edge."""
        off = self.paw_row - OVERLAP
        y_start = self.y + off  # starts OVERLAP px above the paws, so a line the
        #                         cat rests on sits comfortably inside the strip
        pix = QGuiApplication.primaryScreen().grabWindow(
            0, self.x, y_start, CAT_SIZE, LOOKAHEAD)
        if pix.isNull():
            return None
        img = pix.toImage().convertToFormat(QImage.Format_Grayscale8)
        w, h = img.width(), img.height()
        if w == 0 or h == 0:
            return None
        buf = memoryview(img.constBits()).cast("B")
        lo, hi = FOOT_BAND
        cols = [c for c in range(lo, hi, 2) if c < w]  # ~30 sampled columns
        if not cols:
            return None
        masks = self._frame_masks(cols, off)
        r = _flat_line(buf, img.bytesPerLine(), h, cols, masks, VDIFF, CONT_FRAC, FLAT_RANGE)
        return None if r is None else y_start + r


if __name__ == "__main__":
    # Self-check _flat_line (no display needed).
    _w, _rows, _stride = 32, 10, 32
    _cols = list(range(_w))

    _nomask = {c: -1 for c in _cols}  # no cat anywhere

    def _check(label, fill, expect, masks=_nomask):
        buf = bytearray(_w * _rows)
        fill(buf)
        got = _flat_line(memoryview(buf), _stride, _rows, _cols, masks, VDIFF, CONT_FRAC, FLAT_RANGE)
        assert got == expect, f"{label}: expected {expect}, got {got}"

    # uniform flat line (bg 200, a flat row 7 at 40) -> detected at row 7
    def _flat(buf):
        for i in range(len(buf)):
            buf[i] = 200
        for c in range(_w):
            buf[7 * _stride + c] = 40
    _check("flat line", _flat, 7)

    # uniform strip -> nothing
    _check("uniform", lambda b: [b.__setitem__(i, 150) for i in range(len(b))], None)

    # "text-like" row: bg 200, row 7 alternates 40/200 across cols -> non-uniform
    # row (range too big) AND non-continuous edge -> rejected
    def _text(buf):
        for i in range(len(buf)):
            buf[i] = 200
        for c in range(_w):
            buf[7 * _stride + c] = 40 if c % 2 == 0 else 200
    _check("text-like", _text, None)

    # partial-width edge: only 40% of columns step -> below CONT_FRAC -> rejected
    def _partial(buf):
        for i in range(len(buf)):
            buf[i] = 200
        for c in range(0, _w * 4 // 10):
            buf[7 * _stride + c] = 40
    _check("partial edge", _partial, None)

    # the cat itself: a flat opaque bottom edge spanning all columns (rows 0..3),
    # plus a real flat line at row 7. Unmasked, the cat's own bottom transition at
    # row 4 is a phantom flat line; masking the cat (bottom at row 3) must skip it
    # and return the real line at row 7.
    def _cat_plus_line(buf):
        for i in range(len(buf)):
            buf[i] = 200
        for c in range(_w):                    # "cat" body rows 0..3 (flat bottom)
            for r in range(0, 4):
                buf[r * _stride + c] = 30
        for c in range(_w):                    # real line further down
            buf[7 * _stride + c] = 40
    _check("cat unmasked -> phantom", _cat_plus_line, 4)
    _catmask = {c: 3 for c in _cols}           # cat's lowest opaque row = strip row 3
    _check("cat masked, real line", _cat_plus_line, 7, _catmask)

    print("OK: flat-line detection (flat=7; uniform/text/partial rejected; cat masked)")
