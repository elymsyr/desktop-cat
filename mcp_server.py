"""MCP server exposing the cat's local tools (Phase 2).

FastMCP runs in its own asyncio loop on ONE background daemon thread. The tools
touch the GUI (tray, QTimer), which must run on the Qt main thread, so each tool
emits a Qt signal carrying a thunk; a slot owned by the main thread runs it.
Cross-thread signal delivery is auto-queued by Qt — that *is* the marshalling.

One function = one MCP tool = the same action behind the /command (commands.py).
ponytail: one signal carrying a callable, not one signal+slot pair per tool.
"""
import threading

from PySide6.QtCore import QObject, Signal, Slot
from mcp.server.fastmcp import FastMCP

import tools

mcp = FastMCP("catyhoo")
_bridge = None  # set by start(); a _Bridge living on the Qt main thread


class _Bridge(QObject):
    run = Signal(object)  # emitted from the server thread, delivered on main thread

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.run.connect(self._run)  # receiver lives on main thread -> queued

    @Slot(object)
    def _run(self, fn):
        fn(self.ctx)


def _call(fn):
    """Run fn(ctx) on the Qt main thread and return its result (blocking).
    For tools whose return string is the payload, not just a side effect."""
    box = {}
    done = threading.Event()

    def thunk(ctx):
        try:
            box["r"] = fn(ctx)
        finally:
            done.set()

    _bridge.run.emit(thunk)
    done.wait()  # ponytail: no timeout; the GUI loop drains the queue promptly
    return box["r"]


@mcp.tool()
def notify(message: str) -> str:
    """Show a desktop notification."""
    _bridge.run.emit(lambda ctx: tools.notify(ctx, message))
    return "notified"


@mcp.tool()
def time_event(when: str, message: str) -> str:
    """Notify after a relative delay like 5s / 10m / 1h."""
    tools.parse_duration(when)  # validate here so a bad value errors the tool call
    _bridge.run.emit(lambda ctx: tools.time_event(ctx, when, message))
    return f"scheduled in {when}"


@mcp.tool()
def reminder(when: str, message: str) -> str:
    """Notify after a relative delay (5s / 10m / 1h), persisted across restarts."""
    tools.parse_duration(when)  # validate here so a bad value errors the tool call
    _bridge.run.emit(lambda ctx: tools.reminder(ctx, when, message))
    return f"reminder set for {when}"


@mcp.tool()
def workspace_save(name: str) -> str:
    """Save the currently-open apps (Chrome tabs, VS Code folders) under a name."""
    return _call(lambda ctx: tools.workspace_save(ctx, name))


@mcp.tool()
def workspace_list() -> str:
    """List saved workspaces with a short summary of each."""
    return _call(lambda ctx: tools.workspace_list(ctx))


@mcp.tool()
def workspace_run(name: str) -> str:
    """Restore a previously-saved workspace by name."""
    return _call(lambda ctx: tools.workspace_run(ctx, name))


@mcp.tool()
def workspace_remove(name: str) -> str:
    """Permanently delete a saved workspace by name. You MUST call this tool to
    actually remove the workspace — do NOT just say it was removed without calling it."""
    return _call(lambda ctx: tools.workspace_remove(ctx, name))


@mcp.tool()
def clear_book() -> str:
    """Clear all text from the cat's book window."""
    _bridge.run.emit(lambda ctx: tools.clear_book(ctx))
    return "book cleared"


def start(ctx, port=8765):
    """Bind the tools to `ctx` (the CatWindow) and serve over Streamable-HTTP on a
    background daemon thread. Returns the thread."""
    global _bridge
    _bridge = _Bridge(ctx)
    mcp.settings.port = port
    t = threading.Thread(target=lambda: mcp.run(transport="streamable-http"),
                         daemon=True, name="mcp-server")
    t.start()
    return t


if __name__ == "__main__":
    # Headless check: a tool must wrap the right tools.* call behind the bridge.
    # We stub the bridge (no Qt loop) and run the captured thunk against a fake
    # ctx, proving notify() reaches tools.notify with the right message.
    captured = []

    class _StubSignal:
        def emit(self, fn):
            captured.append(fn)

    class _StubBridge:
        run = _StubSignal()

    _bridge = _StubBridge()
    assert notify("hi") == "notified"
    assert time_event("5s", "yo").endswith("5s")

    calls = []

    class _Ctx:
        class tray:
            @staticmethod
            def showMessage(*a):
                calls.append(a)

    captured[0](_Ctx)  # run the notify thunk
    assert calls and calls[0][1] == "hi", calls

    try:
        time_event("abc", "x")
        assert False, "bad duration should raise"
    except ValueError:
        pass

    # workspace tools: _call needs the thunk run *and* its result returned. A
    # bridge whose emit() runs the thunk synchronously against a fake ctx models
    # the Qt main thread draining the queue. Stub providers + temp config so
    # nothing touches real Chrome/VS Code (same trick as tools.py's check).
    import os
    import tempfile

    import config
    import providers

    class _SyncSignal:
        def emit(self, fn):
            fn(_Ctx)  # run on "the main thread" right now

    class _SyncBridge:
        run = _SyncSignal()

    _bridge = _SyncBridge()
    config.CONFIG_PATH = os.path.join(tempfile.mkdtemp(), "config.json")
    config.load()

    class _Fake:
        name = "chrome"
        def detect(self):
            return ["https://a", "https://b"]
        def restore(self, state):
            pass

    providers.PROVIDERS = [_Fake()]
    assert "2 chrome tabs" in workspace_save("work"), "save returns the real summary"
    assert "work" in workspace_list(), "list returns the real saved names"
    assert "restoring 'work'" in workspace_run("work")
    assert workspace_run("missing").startswith("no such")
    assert workspace_remove("work") == "removed 'work'"
    assert "work" not in workspace_list()
    assert workspace_remove("missing").startswith("no such")
    print("OK: mcp tool marshalling + workspace round-trip via _call")
