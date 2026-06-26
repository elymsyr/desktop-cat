"""Local actions the cat can perform. Phase 1: desktop notifications and a
relative one-shot timer. These same functions get registered as MCP tools in
Phase 2 — keep them plain (ctx, *args). Phase 3 adds persisted reminders."""
import time

from PySide6.QtCore import QTimer

import config

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
    print("OK: duration parsing + reminder persistence")
