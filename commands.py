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
    """save/list/run/remove open apps: workspace <save|list|run|remove> <name>"""
    sub, _, name = arg.partition(" ")
    name = name.strip()
    if sub == "list":
        return tools.workspace_list(ctx)
    if sub in ("save", "run", "remove"):
        if not name:
            return f"usage: workspace {sub} <name>"
        return getattr(tools, f"workspace_{sub}")(ctx, name)
    return "usage: workspace <save|list|run|remove> <name>"


def cmd_model(arg, ctx):
    """list or switch the chat model: model [<id>]"""
    if not arg:
        return tools.list_models(ctx)
    return tools.set_model(ctx, arg)


def cmd_reload(arg, ctx):
    """re-read config.json from disk"""
    config.reload()
    return "config reloaded"


def cmd_font(arg, ctx):
    """list or switch the font: font [<order-id>]"""
    fonts = [
        "Pixelmix",
        "Arial",
        "Times New Roman",
        "Courier New",
        "Comic Sans MS",
        "Georgia",
        "Impact",
        "Verdana",
        "Trebuchet MS",
        "Monospace"
    ]
    if not arg:
        current = config.get("font") or "Pixelmix"
        lines = ["Available fonts:"]
        for idx, f in enumerate(fonts, 1):
            marker = "*" if f.lower() == current.lower() else " "
            lines.append(f"{idx}. {f} {marker}")
        lines.append("\nUse /font <order-id> to switch.")
        return "\n".join(lines)

    try:
        order_id = int(arg)
        if order_id < 1 or order_id > len(fonts):
            return f"Invalid font order-id: {arg}. Please choose 1-{len(fonts)}."
        selected = fonts[order_id - 1]
    except ValueError:
        return "Invalid format. Usage: font <order-id>"

    config.set("font", selected)
    config.save()

    if ctx and hasattr(ctx, "set_font_family"):
        if selected == "Pixelmix":
            font_to_apply = ctx.default_font_family
        else:
            font_to_apply = selected
        ctx.set_font_family(font_to_apply)

    return f"font -> {selected}"


def cmd_clear(arg, ctx):
    """clear the book window"""
    tools.clear_book(ctx)
    return None


COMMANDS = {  # alias -> function; extended each phase
    "help": cmd_help,
    "notify": cmd_notify,
    "time-event": cmd_time_event,
    "reminder": cmd_reminder,
    "workspace": cmd_workspace,
    "model": cmd_model,
    "reload": cmd_reload,
    "font": cmd_font,
    "clear": cmd_clear,
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
