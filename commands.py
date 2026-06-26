"""Command dispatch: prefix + alias -> handler.

Each handler takes (arg, ctx) and returns a string to print into the book (or
None). `ctx` is the CatWindow, passed straight through so handlers can reach
ctx.book / ctx.tray etc. in later phases.
ponytail: ctx is the CatWindow, split out only if a non-GUI caller ever needs it.
"""
import config
import tools


def cmd_help(arg, ctx):
    """list the available commands"""
    prefix = config.get("prefix")
    return "\n".join(f"{prefix}{name} — {fn.__doc__ or ''}"
                     for name, fn in COMMANDS.items())


def cmd_notify(arg, ctx):
    """show a desktop notification: notify <message>"""
    if not arg:
        return "usage: notify <message>"
    tools.notify(ctx, arg)
    return None  # the notification itself is the feedback


def cmd_time_event(arg, ctx):
    """notify after a delay: time-event <when> <message>  (e.g. 5s hi)"""
    when, _, msg = arg.partition(" ")
    if not when or not msg.strip():
        return "usage: time-event <when> <message>"
    try:
        tools.time_event(ctx, when, msg.strip())
    except ValueError:
        return f"bad duration: {when}"
    return f"will notify in {when}"


def cmd_reminder(arg, ctx):
    """notify after a delay, surviving restart: reminder <when> <message>"""
    when, _, msg = arg.partition(" ")
    if not when or not msg.strip():
        return "usage: reminder <when> <message>"
    try:
        tools.reminder(ctx, when, msg.strip())
    except ValueError:
        return f"bad duration: {when}"
    return f"reminder set for {when}"


def cmd_workspace(arg, ctx):
    """save/list/run open apps: workspace <save|list|run> <name>"""
    sub, _, name = arg.partition(" ")
    name = name.strip()
    if sub == "list":
        return tools.workspace_list(ctx)
    if sub in ("save", "run"):
        if not name:
            return f"usage: workspace {sub} <name>"
        return getattr(tools, f"workspace_{sub}")(ctx, name)
    return "usage: workspace <save|list|run> <name>"


def cmd_reload(arg, ctx):
    """re-read config.json from disk"""
    config.reload()
    return "config reloaded"


COMMANDS = {  # alias -> function; extended each phase
    "help": cmd_help,
    "notify": cmd_notify,
    "time-event": cmd_time_event,
    "reminder": cmd_reminder,
    "workspace": cmd_workspace,
    "reload": cmd_reload,
}


def dispatch(text, ctx):
    """Run `text` as a command if it starts with the configured prefix; otherwise
    echo it back. Returns the string to show in the book, or None."""
    prefix = config.get("prefix")
    if not text.startswith(prefix):
        return text
    name, _, arg = text[len(prefix):].partition(" ")
    fn = COMMANDS.get(name)
    if fn is None:
        return f"unknown command: {name}"
    return fn(arg.strip(), ctx)


if __name__ == "__main__":
    assert "help" in dispatch("/help", None), "help lists itself"
    assert dispatch("/nope", None).startswith("unknown"), "unknown reported"
    assert dispatch("plain text", None) == "plain text", "non-command echoes"
    print("OK: command dispatch")
