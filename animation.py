"""Animation assets + state-machine table for catyhoo.

Ported from the legacy tkinter cat. The animation is a state machine, not a
timeline: EVENTS maps an event-cycle number to
    [[sub-event/frame sequence], [allowed next event-cycles]]
The values inside the sequence are *image indices* into the sorted gif list
(see IMAGE_ORDER) — that positional mapping is load-bearing, so we assert it.
"""
import os

from PIL import Image
from PySide6.QtGui import QImage, QPixmap

MEDIA = os.path.join(os.path.dirname(__file__), "media")
GIFS_DIR = os.path.join(MEDIA, "gifs")
FALLING_GIF = os.path.join(MEDIA, "gifs_others", "falling.gif")

CAT_SIZE = 160

# Expected gif order after sorted(os.listdir). event_number indexes this list,
# with "falling" appended at the end (index 20).
IMAGE_ORDER = [
    "L_goosebumps.gif", "L_idle.gif", "L_idle2.gif", "L_jump.gif",
    "L_licking.gif", "L_licking2.gif", "L_sleep.gif", "L_touch.gif",
    "L_walk.gif", "L_walk2.gif",
    "R_goosebumps.gif", "R_idle.gif", "R_idle2.gif", "R_jump.gif",
    "R_licking.gif", "R_licking2.gif", "R_sleep.gif", "R_touch.gif",
    "R_walk.gif", "R_walk2.gif",
]

EVENTS = {  # eventNumber: [[actionOrder], [possibleNextEventNumbers]]
    # Left events
    0: [[1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 4, 4, 4, 4, 1, 1, 1, 1, 2, 2], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]],  # idle 1
    1: [[2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]],  # idle 2
    2: [[8, 8, 8], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]],  # walk 1
    3: [[9, 9, 9], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]],  # walk 2
    4: [[3], [0, 1, 2, 3, 8, 9]],  # jump
    5: [[6, 6, 6], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 5, 5, 5, 18, 20]],  # sleep
    6: [[7], [0, 1, 4, 7, 7, 7, 7, 8, 9, 12]],  # touch
    7: [[0], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14, 0, 1, 0, 1]],  # goosebumps
    # Right events
    8: [[11, 11, 11, 11, 12, 12, 12, 12, 11, 11, 14, 14, 14, 14, 11, 11, 11, 11, 12, 12], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]],  # idle 1 R
    9: [[12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 15, 15, 15, 15, 15, 15, 15, 11, 11, 11], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]],  # idle 2 R
    10: [[18, 18, 18], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]],  # walk 1 R
    11: [[19, 19, 19], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]],  # walk 2 R
    12: [[13], [0, 1, 10, 11, 8, 9]],  # jump R
    13: [[16, 16, 16], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 16, 16, 16, 18, 20]],  # sleep R
    14: [[17], [0, 1, 4, 8, 9, 12, 15, 15, 15, 15]],  # touch R
    15: [[10], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14]],  # goosebumps R
    # Extra events
    16: [[1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 1, 1, 1, 1, 11, 11, 11, 11, 12, 12, 12, 12, 12], [0, 1, 8, 9, 5, 17, 18, 19, 20]],  # idle 3
    17: [[2, 2, 2, 2, 2, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 14, 14, 14, 14, 14, 14, 14, 12, 12, 11, 11, 11], [0, 1, 8, 9, 5, 16, 18, 19, 20]],  # idle 4
    18: [[12, 12, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16], [0, 1, 8, 9]],  # sleep long
    19: [[8, 8, 19, 19, 9, 9, 18, 18], [0, 1, 8, 9, 16, 17, 18, 20]],  # walk there
    20: [[3, 0, 10], [16, 17, 18, 19]],  # jump and goosebumps
    21: [[20], [21]],  # falling
    22: [[7], [23, 24]],  # stay put
    23: [[4], [23, 24]],  # stay put continue
    24: [[2], [24]],  # stay put continue
    25: [[6], [25]],  # long sleep
}


def _frame_count(name):
    if "walk" in name or "goosebumps" in name:
        return 8
    if "touch" in name:
        return 6
    if "jump" in name:
        return 7
    return 4


def _slice_gif(path, n):
    """Slice n frames of a gif into QPixmaps, color-keying black -> transparent.

    The legacy app used tkinter's transparentcolor='black', so every fully-black
    pixel is treated as transparent. We reproduce that exactly.
    # ponytail: one-time per-pixel pass; trivial for ~21 small gifs.
    """
    img = Image.open(path)
    pixmaps = []
    for i in range(n):
        img.seek(i)
        rgba = img.convert("RGBA")
        rgba.putdata([
            (0, 0, 0, 0) if (r, g, b) == (0, 0, 0) else (r, g, b, a)
            for r, g, b, a in rgba.getdata()
        ])
        w, h = rgba.size
        qimg = QImage(rgba.tobytes("raw", "RGBA"), w, h, QImage.Format_RGBA8888)
        pixmaps.append(QPixmap.fromImage(qimg.copy()))  # copy: detach from buffer
    return pixmaps


def load_frames():
    """Return (images, frames) where images[event_number] -> key into frames."""
    images = sorted(os.listdir(GIFS_DIR))
    assert images == IMAGE_ORDER, (
        f"gif set/order changed; event_number mapping is now wrong.\n"
        f"expected {IMAGE_ORDER}\ngot      {images}"
    )
    frames = {name: _slice_gif(os.path.join(GIFS_DIR, name), _frame_count(name))
              for name in images}
    images = images + ["falling"]
    frames["falling"] = _slice_gif(FALLING_GIF, 4)
    return images, frames


def colorkey_pixmap(path):
    """Load a PNG with black->transparent (for book/prompt backgrounds)."""
    rgba = Image.open(path).convert("RGBA")
    rgba.putdata([
        (0, 0, 0, 0) if (r, g, b) == (0, 0, 0) else (r, g, b, a)
        for r, g, b, a in rgba.getdata()
    ])
    w, h = rgba.size
    qimg = QImage(rgba.tobytes("raw", "RGBA"), w, h, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg.copy())


if __name__ == "__main__":
    # Self-check: asset order matches the load-bearing event_number mapping,
    # and every event number referenced by EVENTS sequences has a frame list.
    assert sorted(os.listdir(GIFS_DIR)) == IMAGE_ORDER, "gif order mismatch"
    images = IMAGE_ORDER + ["falling"]
    used = {n for cyc in EVENTS.values() for n in cyc[0]}
    assert max(used) < len(images), f"event index {max(used)} >= {len(images)} images"
    for name in IMAGE_ORDER:
        assert _frame_count(name) >= 1
    print(f"OK: {len(images)} images, event indices {min(used)}..{max(used)} all in range")
