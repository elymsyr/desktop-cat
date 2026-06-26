# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`catyhoo` — a cross-platform (PySide6) pixel-art desktop cat that walks on the
screen edge, runs `/commands` from an in-app prompt, and exposes those same
commands as **MCP tools**. The two headline features (see [FEATURES.md](FEATURES.md)):

1. **MCP integration** — the cat hosts its own MCP server; every capability is one tool function reachable *both* over MCP and via a `/command`.
2. **Workspace management** — save the currently-open apps (Chrome tabs, VS Code folders) under a name and restore them later.

**Designed Linux-first, OS-agnostic by construction.** Everything uses Qt
notifications, HTTP/CDP, the `code` CLI, and stdlib `json`/`urllib`/`asyncio`.
The only OS-specific logic lives *inside* a provider's `detect()`/`restore()`.

> NOTE: This is a ground-up rewrite. The old Windows-only `tkinter` monolith
> (`desktop-cat/` + `cat/` trees) is **gone** — ignore any reference to it. The
> README still describes the legacy "Workload" app and is stale; trust
> [FEATURES.md](FEATURES.md) and [ROADMAP.md](ROADMAP.md) instead.

## Run

```bash
pip install -r requirements.txt   # PySide6, Pillow, mcp
python main.py
```

Python > 3.11. No test framework, linter, or build step.

## Tests = per-module `__main__` self-checks

Every non-trivial logic module carries one `assert`-based self-check in its
`if __name__ == "__main__":` block (no pytest, no fixtures). Run them directly:

```bash
python config.py && python tools.py && python commands.py && python mcp_server.py
# each prints one "OK: ..." line on success
```

When you add logic, add/extend that module's self-check — it's the only test
layer. `tools.py`'s check rebinds `_arm`/`notify` to no-ops so reminder
persistence can be verified with no Qt event loop or tray.

## Architecture

**Single source of truth per capability.** A capability is one plain function
`f(ctx, *args)` in [tools.py](tools.py). It is reached two ways, and both go
through it unchanged:
- `/command` typed in the prompt → [commands.py](commands.py) `dispatch()` → handler → `tools.f(ctx, ...)`.
- External MCP client → [mcp_server.py](mcp_server.py) `@mcp.tool()` → marshalled to main thread → `tools.f(ctx, ...)`.

**`ctx` is the `CatWindow` itself** (passed straight through). Handlers reach
`ctx.tray` / `ctx.book` etc. directly — no extra abstraction. (`ponytail:`
split out only if a non-GUI caller ever needs commands.)

**MCP threading model** ([mcp_server.py](mcp_server.py)): FastMCP runs its
asyncio loop on **one** background daemon thread (Streamable-HTTP, default port
8765 — the cat is a persistent process clients *attach to*, so not stdio). Qt
GUI work must stay on the main thread, so each tool emits `_Bridge.run`
(a `Signal(object)` carrying a thunk); Qt's queued cross-thread delivery **is**
the marshalling. One signal carries any callable — no signal/slot pair per tool.

**Command dispatch** ([commands.py](commands.py)): `COMMANDS` is a flat
`alias -> handler(arg, ctx)` dict. `dispatch(text, ctx)` returns text unchanged
if it doesn't start with `config.get("prefix")` (preserves plain-text echo),
else looks up the alias. Handler **docstrings are the help text** — `cmd_help`
generates the list from them, no separate help table. A handler returns a string
to print into the book, or `None` (e.g. when the notification itself is the feedback).

**Config** ([config.py](config.py)): one JSON file (`config.json`, created
lazily on first `save()`, gitignored). `load()` merges disk over `DEFAULTS`;
corrupt/missing → defaults. `reload = load` — re-reading from disk *is* live
reload. Holds `prefix`, `reminders`, and (later) `workspaces`.

**Persistence pattern** (reminders, [tools.py](tools.py)): store the
**absolute** epoch fire time in config. `arm_reminders(ctx)` re-arms everything
pending at startup (overdue → fires ~now); `_fire` drops the entry from the
persisted list post-fire so it can't refire next launch. `cat.py` calls
`arm_reminders` **after** `_make_tray()` (firing touches `ctx.tray`).

**Visual shell** (already complete): [cat.py](cat.py) `CatWindow` owns three
frameless translucent always-on-top widgets — the cat, the prompt box
([prompt.py](prompt.py)), the help book ([book.py](book.py)) — glued together
on screen. Animation ([animation.py](animation.py)) is a **state machine**: an
event maps to a frame sequence + allowed next events; the next event is chosen
randomly, biased by x-position (turn at edges) and flags. GIF assets live in
`media/`.

## Roadmap discipline

[ROADMAP.md](ROADMAP.md) drives the work **one reviewed phase at a time** —
"Each phase is reviewed and approved before the next." Do not start the next
phase without explicit approval. Status: Phases 0–3 (foundation, local tools,
MCP server, persistence) are done; **Phase 4 — Workspace providers** is next.

Provider contract is a plain `Protocol` + a list (no registry):
`name`, `detect() -> state | None`, `restore(state)`. Adding an app source =
one more provider object in the list.

## Conventions (`ponytail` mode)

The codebase is written lazy-but-correct: stdlib first, no speculative
abstraction, shortest working diff. Deliberate simplifications are marked with
`ponytail:` comments naming the ceiling and upgrade path — treat them as intent,
not omissions. Keep new code in the same style; don't add dependencies for what
a few stdlib lines do.

## CodeGraph

A `.codegraph/` directory exists — reach for CodeGraph BEFORE grep/find when
locating or understanding code. Shell (always works):
`codegraph explore "<symbols or question>"` and `codegraph node <symbol-or-file>`.
MCP tools `codegraph_explore` / `codegraph_node` give the same output when available.
