"""Local actions the cat can perform. Phase 1: desktop notifications and a
relative one-shot timer. These same functions get registered as MCP tools in
Phase 2 — keep them plain (ctx, *args). Phase 3 adds persisted reminders."""
import json
import threading
import time
import urllib.request

from PySide6.QtCore import QObject, QTimer, Signal

import config
import providers

_UNITS = {"s": 1, "m": 60, "h": 3600}


def parse_duration(when):
    """'5s' / '10m' / '1h' / '3' (bare = seconds) -> milliseconds. Raises ValueError."""
    when = when.strip().lower()
    if when and when[-1] in _UNITS:
        num, mult = when[:-1], _UNITS[when[-1]]
    else:
        num, mult = when, 1
    return int(float(num) * mult * 1000)


def notify(ctx, msg, title="catyhoo"):
    """Desktop notification via the tray icon."""
    ctx.tray.showMessage(title, msg)


def time_event(ctx, when, msg):
    """Fire notify(msg) once after `when` (relative). Returns the delay in ms."""
    ms = parse_duration(when)
    QTimer.singleShot(ms, lambda: notify(ctx, msg))
    return ms


def reminder(ctx, when, msg):
    """Like time_event but persisted to config, so it survives a restart. Stores
    the absolute fire time; arm_reminders() re-arms whatever's still pending."""
    fire_at = time.time() + parse_duration(when) / 1000
    _save_reminders(_pending() + [{"at": fire_at, "msg": msg}])
    _arm(ctx, fire_at, msg)
    return fire_at


def arm_reminders(ctx):
    """Re-arm every persisted reminder at startup. Overdue ones fire ~now."""
    for r in _pending():
        _arm(ctx, r["at"], r["msg"])


def _arm(ctx, fire_at, msg):
    ms = max(0, int((fire_at - time.time()) * 1000))
    QTimer.singleShot(ms, lambda: _fire(ctx, fire_at, msg))


def _fire(ctx, fire_at, msg):
    notify(ctx, msg)
    _save_reminders([r for r in _pending() if r["at"] != fire_at])


# ---- LLM chat (Open WebUI, OpenAI-compatible) ------------------------------
# The blocking HTTP call runs on a worker thread; the answer is marshalled back
# to the Qt main thread via a signal, the same pattern _Bridge uses in
# mcp_server.py. GUI-only, single-turn (ponytail: no history/streaming yet).

class _Reply(QObject):
    done = Signal(str)


_replies = set()  # keep reply objects alive until their answer lands


def _api(path, payload=None):
    """GET (payload=None) or POST JSON to Open WebUI; returns parsed JSON. Blocking."""
    url = config.get("openwebui_url").rstrip("/") + path
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Authorization": "Bearer " + config.get("openwebui_key")}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data, headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def ask(ctx, prompt):
    """Send `prompt` to the current model on a worker thread; the answer is
    appended to the book when it arrives (does not block the GUI). Returns None."""
    reply = _Reply()
    _replies.add(reply)

    def finish(answer):
        ctx.book_append(answer)
        _replies.discard(reply)

    reply.done.connect(finish)  # created on main thread -> queued delivery

    def worker():
        try:
            r = _api("/api/chat/completions", {
                "model": config.get("model"),
                "messages": [{"role": "user", "content": prompt}],
                "stream": False})
            answer = r["choices"][0]["message"]["content"].strip()
        except Exception as e:  # network down, auth, bad JSON, timeout
            answer = f"llm error: {e}"
        reply.done.emit(answer)

    threading.Thread(target=worker, daemon=True, name="openwebui").start()
    return None


def list_models(ctx):
    """Return the available model ids, marking the current one with '*'."""
    ids = [m["id"] for m in _api("/api/models")["data"]]
    cur = config.get("model")
    return "\n".join(("* " if i == cur else "  ") + i for i in ids)


def set_model(ctx, name):
    """Switch the active model and persist it."""
    config.set("model", name)
    config.save()
    return f"model -> {name}"


# ---- workspaces (Phase 4) --------------------------------------------------
# One capability = one function; same functions become MCP tools in Phase 5.
# State per workspace is {provider.name: detected_state}; each provider knows how
# to detect/restore its own piece (providers.py).

def workspace_save(ctx, name):
    """Detect every provider's current state and store it under `name`."""
    state = {}
    for p in providers.PROVIDERS:
        s = p.detect()
        if s:
            state[p.name] = s
    ws = dict(config.get("workspaces") or {})
    ws[name] = state
    config.set("workspaces", ws)
    config.save()
    return f"saved '{name}': {_summary(state)}" if state else f"saved '{name}': nothing open to capture"


def workspace_list(ctx):
    """One line per saved workspace with a short summary, or a hint if none."""
    ws = config.get("workspaces") or {}
    if not ws:
        return "no saved workspaces"
    return "\n".join(f"{name} — {_summary(state)}" for name, state in ws.items())


def workspace_run(ctx, name):
    """Restore each provider's saved state for `name`."""
    ws = config.get("workspaces") or {}
    if name not in ws:
        return f"no such workspace: {name}"
    state = ws[name]
    for p in providers.PROVIDERS:
        if p.name in state:
            p.restore(state[p.name])
    return f"restoring '{name}': {_summary(state)}"


def _summary(state):
    # state values are lists (urls / folder paths); name them per provider.
    label = {"chrome": "chrome tabs", "vscode": "vscode folders"}
    parts = [f"{len(v)} {label.get(k, k)}" for k, v in state.items()]
    return ", ".join(parts) if parts else "empty"


def _pending():
    return list(config.get("reminders") or [])  # copy: never mutate the stored list


def _save_reminders(reminders):
    config.set("reminders", reminders)
    config.save()


if __name__ == "__main__":
    assert parse_duration("5s") == 5000
    assert parse_duration("10m") == 600000
    assert parse_duration("1h") == 3600000
    assert parse_duration("3") == 3000, "bare number = seconds"
    try:
        parse_duration("abc")
        assert False, "bad input should raise"
    except ValueError:
        pass

    # reminder persistence, without a Qt loop: rebind _arm/notify (running as a
    # script, these globals ARE what reminder()/_fire() call) so nothing schedules
    # or touches a tray; prove reminder() saves and _fire() removes it.
    import os
    import tempfile
    config.CONFIG_PATH = os.path.join(tempfile.mkdtemp(), "config.json")
    config.load()
    _arm = lambda *a: None      # noqa: E731
    notify = lambda *a: None    # noqa: E731
    at = reminder(None, "1h", "drink water")
    assert config.reload()["reminders"][0]["msg"] == "drink water"
    _fire(None, at, "drink water")
    assert config.reload()["reminders"] == [], "fired reminder is dropped"

    # workspaces: stub providers so save/list/run round-trip through config with
    # no Chrome/VS Code. restore records what it was handed.
    restored = []

    class _Fake:
        name = "chrome"
        def detect(self):
            return ["https://a", "https://b"]
        def restore(self, state):
            restored.append(state)

    providers.PROVIDERS = [_Fake()]
    assert "2 chrome tabs" in workspace_save(None, "work")
    assert config.reload()["workspaces"]["work"]["chrome"] == ["https://a", "https://b"]
    assert "work — 2 chrome tabs" in workspace_list(None)
    workspace_run(None, "work")
    assert restored == [["https://a", "https://b"]], restored
    assert workspace_run(None, "missing").startswith("no such")

    # LLM: stub _api so nothing hits the network. ask() delivers via a queued
    # signal, so drive one Qt event-loop pass to let it land in the fake book.
    from PySide6.QtWidgets import QApplication
    _app = QApplication.instance() or QApplication([])

    _api = lambda path, payload=None: {  # noqa: E731
        "choices": [{"message": {"content": " hi there "}}],
        "data": [{"id": "llama3.1:8b"}, {"id": "other"}],
    }

    class _Book:
        seen = []
        def book_append(self, t):
            _Book.seen.append(t)

    book = _Book()
    ask(book, "yo")
    for _ in range(100):  # let the worker emit, then deliver the queued signal
        _app.processEvents()
        if book.seen:
            break
        time.sleep(0.01)
    assert book.seen == ["hi there"], book.seen  # stripped answer

    models = list_models(None)
    assert "* llama3.1:8b" in models and "  other" in models, models

    assert set_model(None, "other") == "model -> other"
    assert config.reload()["model"] == "other", "model switch persists"

    print("OK: duration parsing + reminder persistence + workspace save/list/run + llm chat")
