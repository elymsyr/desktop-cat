# Stripped features (to re-add later)

`catyhoo/` is the cross-platform (PySide6) rewrite. v1 keeps **only the
visuals**: the animated walking cat, drag, tray (exit/show), an **empty** command
prompt shell, and the help book. Every *system* feature from the old Windows
tkinter app (`desktop-cat/`, `cat/`) was intentionally left out. They are listed
here with what they did and the agreed cleaner way to bring them back.

The old trees are untouched — they remain the reference implementation.

## 1. Command parser / commands / prefix
- **Was:** text typed in the prompt was parsed if it started with a prefix
  (`*`). Legacy `parser()` = big if/elif; rewrite `Parser` used an
  alias→`{help, func}` dict. (`cat/custom_parser.py`, `cat/parser_functions.py`)
- **Re-add:** keep the alias→`{help, func}` dict. Wire `PromptWindow._submit`
  (currently just echoes into the book) to dispatch through it. Cross-platform —
  no Windows dependency.

## 2. Workload — VSCode capture/restore
- **Was:** discovered open VSCode projects by scraping window **titles** via
  `pygetwindow` (`findVSCode`, title format `file - project - Visual Studio
  Code`); restore ran `code .` per saved path. (`cat/workload.py`,
  `desktop-cat/workload.py`)
- **Re-add (cleaner, Linux/Wayland-safe):** a small **VSCode extension** that
  reports the open workspace folder(s) to the app, plus **`watchdog`** (inotify
  on Linux) to watch those folders for live file changes. Avoids fragile,
  X11-only window-title scraping.

## 3. Workload — Chrome open tabs
- **Was:** two strategies. Active one brute-forced through tabs with
  `ctrl+tab`/`ctrl+l`/`ctrl+c` clipboard scraping (`get_open_tabs_urls`); the
  other read Chrome's on-disk `History` sqlite DB (`findChrome`) — but that gives
  *visited* URLs, not *open* tabs.
- **Re-add (no tab-walking):** **Chrome DevTools Protocol** — launch/attach Chrome
  with `--remote-debugging-port=9222`, then `GET http://localhost:9222/json` lists
  every open tab's title+URL in one request. Alternative: a browser **extension**
  using the `chrome.tabs` API (the existing `desktop-cat/extension_cat/` is a
  starting point).

## 4. Config (JSON)
- **Was:** a single JSON file holding `config` (prefix, fonts, chrome paths),
  `workload_data` (project→path map), and `workloads`; live `reload_config()`;
  `*config e` opened it in the OS editor. Accessed via `settings.functions`
  (`find_key`, `reset_file`). (`cat/settings/`, `cat/data/config-test.json`)
- **Re-add:** a small JSON loader (stdlib `json`) for prefix/fonts/saved
  workloads. Drop the Windows-specific Chrome path keys in favor of the
  DevTools/extension approach above.

## 5. Notifications
- **Was:** `Notify` class drawing in-app notification images
  (`media/notify/*.png`). (`cat/notify.py`)
- **Re-add:** `QSystemTrayIcon.showMessage` (native, cross-platform), or keep the
  in-app image popups as a translucent Qt window if the visual style matters.

## 6. Misc commands
- Google search command, DND / silent-notification toggles, sleep toggle, tray
  command — all were parser commands (`cat/parser_functions.py`). Re-add as
  entries in the commands dict from §1.

## Kept in v1 (for reference)
Animated cat (full EVENTS state machine), left/right facing, jump/sleep/touch/
licking/goosebumps/idle/walk/falling, per-pixel transparency (black→transparent),
always-on-top frameless windows, walking along the bottom of the screen, drag,
tray show/exit, empty prompt shell, help book.
