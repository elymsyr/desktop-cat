# Features

`catyhoo` is the cross-platform (PySide6) desktop cat. Two features are the
sole focus from here on. Both are **designed Linux-first** — they must work
flawlessly and robustly on Linux — but every tool and architectural choice is
deliberately OS-agnostic so macOS/Windows support is a later drop-in, not a
rewrite.

The cat already ships its visuals: animated walking cat, drag, tray
(show/exit), the command prompt shell, and the help book. These two features
build on top of that shell.

---

## 1. Model Context Protocol (MCP) integration

**The cat exposes its own MCP server.** Its capabilities — notifications,
scheduling, reminders, workspace operations, and anything added later — are MCP
tools. They are callable two ways from one implementation:

- by **external MCP clients** (e.g. Claude Desktop / Claude Code) that connect
  to the running cat, and
- by the **in-app prompt** — typing a `/command` invokes the *same* tool
  function locally.

### Architecture

- **SDK:** the Python `mcp` SDK (FastMCP). A tool is one decorated function;
  registering it exposes it over MCP **and** makes it available as a slash
  command — no per-tool plumbing. This is what delivers "full access to all
  available MCP features": whatever tools the cat registers are all reachable.
- **Transport:** Streamable-HTTP / SSE on a local port. The cat is a persistent
  GUI process that clients *attach to*, not one a client spawns — so stdio
  (spawn-per-client) is the wrong fit.
- **Threading:** the MCP server (asyncio) runs on a single background thread.
  Tool calls that touch the GUI are marshalled onto the Qt main thread via a
  queued signal (Qt GUI work must stay on the main thread). One thread, no
  pool.
- **Prompt dispatch:** a small alias → tool-function map replaces the current
  echo in `_submit` ([prompt.py:37](prompt.py#L37), wired through `book_append`
  at [cat.py:197](cat.py#L197)). Tool output / confirmations print to the help
  book via `BookWindow.append_text` ([book.py:35](book.py#L35)).

### Built-in tools (and their prompt aliases)

| Tool | Alias | What it does |
|------|-------|--------------|
| `notify` | `/notify <msg>` | Native desktop notification via `QSystemTrayIcon.showMessage` ([cat.py:185](cat.py#L185)). |
| `time_event` | `/time-event <when> <msg>` | A `QTimer`-backed one-shot/relative timer that fires a `notify` when it elapses. |
| `reminder` | `/remind <when> <msg>` | Like `time_event`, but persisted (see config below) so it survives a restart. |
| `workspace_*` | `/workspace …` | Save / list / restore workspaces — shared with feature 2. |

**Linux note:** notifications go through Qt → libnotify/D-Bus. No
Windows-specific calls anywhere in this feature.

---

## 2. Workspace management

Detect the currently active applications and their state, save that state under
a name, and restore it later to pick up exactly where you left off.

### Pluggable providers

Each application type is a **provider** behind a tiny duck-typed contract:

```
name            -> str
detect()        -> state           # capture current state, or None if app absent
restore(state)  -> None            # bring the app back to that state
```

The app holds a plain list of provider objects. Adding a new app source = write
one more provider. (Plain Protocol + list, not a plugin/registry framework.)

Two providers ship first:

- **ChromeProvider (Linux-first).** Detect open tabs via the **Chrome DevTools
  Protocol**: Chrome runs with `--remote-debugging-port=9222`, then a single
  `GET http://localhost:9222/json` (stdlib `urllib`) returns every open tab's
  title + URL. Restore launches Chrome with the saved URLs. No clipboard
  tab-walking and no reading the on-disk `History` sqlite DB.
- **VSCodeProvider (Linux-first).** Detect open folders by reading VS Code's
  workspace storage / running-instance info — *not* fragile, X11-only window
  title scraping. Restore runs `code <path>` per saved folder.

### Commands

| Command | Behaviour |
|---------|-----------|
| `/workspace save <name>` | Run every provider's `detect()`, store the combined result under `<name>`. |
| `/workspace list` | Print saved workspace names + a short summary into the book. |
| `/workspace run <name>` | Call each provider's `restore(state)` for the saved entry. |

These operations are also registered as MCP tools (feature 1), so an external
client can save and restore workspaces too.

### Persistence

A single JSON file (stdlib `json`) holds `workspaces` and `reminders`
(from feature 1). It is live-reloadable.

---

## Cross-platform stance

The chosen tools are OS-agnostic: Qt notifications, the DevTools Protocol over
HTTP, the `code` CLI, and stdlib `json` / `urllib` / `asyncio`. The only
OS-specific logic is *inside* each provider's `detect()`/`restore()`, behind the
provider contract — so a future macOS or Windows variant slots in without
touching the rest of the system.
