"""Single JSON config file: load / save / live reload (stdlib json only)."""
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULTS = {"prefix": "/", "reminders": [], "workspaces": {}}  # new keys land here as later phases need them

_config = dict(DEFAULTS)


def load():
    """Read the config from disk, merged over DEFAULTS. Missing/corrupt file ->
    defaults. Re-reading is also how live reload works (see `reload`)."""
    global _config
    try:
        with open(CONFIG_PATH) as f:
            _config = {**DEFAULTS, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        _config = dict(DEFAULTS)
    return _config


def save():
    with open(CONFIG_PATH, "w") as f:
        json.dump(_config, f, indent=2)


def get(key):
    return _config.get(key, DEFAULTS.get(key))


def set(key, value):
    _config[key] = value


reload = load  # re-reading from disk *is* live reload


# ponytail: no config.json is committed; it's created lazily on the first save().
if __name__ == "__main__":
    import tempfile

    CONFIG_PATH = os.path.join(tempfile.mkdtemp(), "config.json")
    assert load() == DEFAULTS, "no file -> defaults"
    assert get("prefix") == "/"
    _config["prefix"] = "*"
    save()
    assert reload()["prefix"] == "*", "saved value round-trips through reload()"
    set("reminders", [{"at": 1, "msg": "x"}])
    save()
    assert reload()["reminders"][0]["msg"] == "x", "reminders persist"
    assert get("missing") is None, "unknown key falls back to None"
    print("OK: config load/save/reload")
