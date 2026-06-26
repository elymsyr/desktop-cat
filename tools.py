"""Local actions the cat can perform. Phase 1: desktop notifications and a
relative one-shot timer. These same functions get registered as MCP tools in
Phase 2 — keep them plain (ctx, *args). Phase 3 adds persisted reminders."""
import time

from PySide6.QtCore import QTimer

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
    print("OK: duration parsing + reminder persistence + workspace save/list/run")
