# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Windows desktop pet: a pixel-art cat that walks along the taskbar and runs commands typed into a small in-app prompt. The headline feature is **Workload** — save the currently-open VSCode windows + Chrome tabs under a name, then restore them all later.

**Windows-only.** It relies on `wm_attributes('-transparentcolor', ...)` (Windows tkinter only), `pygetwindow`/`pyautogui` window scraping, Chrome's on-disk `History` sqlite DB, and hardcoded `C:/...` / backslash paths. It will not run as-is on Linux/macOS.

## Two parallel source trees

- `desktop-cat/` — the **legacy** monolith. Everything lives in one `DesktopCat` class in `main.py` (~620 lines). This is what the README's "Run Locally" points at and what the demo0 release was built from.
- `cat/` — the **in-progress modular rewrite** ("will be changed soon" in commits). Same EVENTS animation engine, but split into collaborating classes: `Parser` (`custom_parser.py`), `MessageBox`, `Workbook`, `Workload`, `Notify`, with `desktop_cat.py` as entry. New work generally belongs here; confirm which tree before editing.

The `z*.py` files in `desktop-cat/` (`zworkload.py`, `zparser.py`, etc.) are experimental/scratch versions — not imported by `main.py`.

## Run

```bash
# legacy
cd desktop-cat && python main.py
# rewrite
cd cat && python desktop_cat.py
```

Python > 3.11. There is no test suite, linter, or build step beyond packaging. `setup.py` / the `auto-py-to-exe` + `pyinstaller` deps are only for producing the Windows .exe release; use `set.py`'s `resource_path()` for any bundled-asset paths so they resolve under PyInstaller's `_MEIPASS`.

Dependencies: `desktop-cat/requirements.txt` is minimal (pillow, pyglet, pystray); `cat/requirements.txt` is a full frozen env (selenium, eel, pyautogui, etc.) — install the one for the tree you're running.

## Architecture

**Animation is a state machine, not a timeline.** `EVENTS` (defined in `desktop-cat/set.py` and inline in `cat/desktop_cat.py`) maps an event number to `[[frame/sub-event sequence], [allowed next events]]`. `update()` runs on `window.after(...)` (no real thread), advances `cycle` through the current event's frames, then `choose_event_change()` picks the next event randomly from the allowed list — biased by the cat's x position (turn around near screen edges) and flags like `long_sleep`/`falling`/`command_created`. Left- and right-facing actions are separate event numbers (e.g. idle=0/1 left, 8/9 right). GIF frames are pre-sliced per-file in `load_images()`; the frame count per gif is hardcoded by filename keyword (`walk`→8, `touch`→6, `jump`→7, else 4).

**Three transparent always-on-top tkinter windows:** the cat (`window`), the command prompt (`command_prompt`), and the help "book" (`book`). All use `overrideredirect(True)` + transparent-color black. Their positions are kept glued to the cat by `pos_cp()` / `pos_book()` called every `update()`.

**Command flow:** text typed in the prompt is parsed only if it starts with the prefix (`*` legacy, configurable). Legacy `parser()` is a big if/elif over `message[0]`; the rewrite's `Parser` uses a `commands` dict mapping aliases → `{help, func}`. Commands: workload save/run/list, sleep toggle, tray, config edit/reload, google search, help/book.

**Workload save/restore** (`workload.py` in both trees):
- VSCode: discovered by parsing window *titles* via `pygetwindow` (`findVSCode`), so detection depends on the title format `file - project - Visual Studio Code`. Restore = `subprocess.run(["code", "."])` per saved project path.
- Chrome tabs: two strategies exist — `get_open_tabs_urls()` brute-forces through tabs with `ctrl+tab`/`ctrl+l`/`ctrl+c` clipboard scraping (active, used in `save_workload`), and `findChrome()` reads the Chrome `History` sqlite DB by copying it first (since Chrome locks it). The clipboard one is what's wired up; the History path is mostly dead/alternative.
- Saved workloads + learned project paths persist to the config JSON (`data/config-test.json`). There's a companion unpacked Chrome extension in `desktop-cat/extension_cat/` that lists open tabs — an alternate tab source, not yet integrated.

**Config** is a single JSON file (`CONFIG_PATH` in `set.py`) holding `config` (prefix, fonts, chrome paths/profile), `workload_data` (remembered project→path map), and `workloads` (saved sessions). `reload_config()` re-reads it live; `*config e` opens it in the OS editor.

## Gotchas

- Paths in `set.py` are relative with Windows backslashes and assume the cwd is the tree root — run from inside `desktop-cat/` or `cat/`, not the repo root.
- `INITIAL_X`/`INITIAL_Y` (1400/922) and the drag clamps assume a specific screen resolution; the cat sits at a fixed taskbar y.
- Dragging the cat fast breaks the animation loop (known bug, surfaced in the in-app help text).
- Comments and some `print` debug output are in Turkish (`get_chrome_recently_visited_sites`).

## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tools** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them. `codegraph_node` returns one symbol's source + callers, or reads a whole file with line numbers. If the tools are listed but deferred, load them by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` and `codegraph node <symbol-or-file>` print the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.