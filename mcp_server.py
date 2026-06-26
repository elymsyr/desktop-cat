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
    print("OK: mcp tool marshalling")
