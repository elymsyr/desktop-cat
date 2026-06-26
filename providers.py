"""Workspace providers (Phase 4): capture the currently-open apps and restore
them later. Each provider is a plain duck-typed object with `name`, `detect()`
and `restore(state)` — a Protocol + a list, no registry (FEATURES.md §2).

Chrome tabs can't be read via CDP anymore: Chrome >=136 ignores
`--remote-debugging-port` on the default profile (security mitigation). Instead a
tiny MV3 extension (see extension/) PUSHes the open-tab list to the local
receiver below; ChromeProvider.detect() just reads the latest snapshot.
ponytail: stdlib http.server on its own port, decoupled from the MCP server.
"""
import json
import shutil
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Protocol

RECEIVER_PORT = 8766
STALE_SECS = 150  # no push within this -> Chrome assumed closed (extension beats 60s)

_lock = threading.Lock()
_latest_tabs = None   # list[{"title","url"}] | None
_last_seen = 0.0      # epoch of the last POST


class Provider(Protocol):
    name: str
    def detect(self): ...
    def restore(self, state): ...


# ---- Chrome tab receiver (fed by the extension) ----------------------------
class _TabsHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global _latest_tabs, _last_seen
        if self.path != "/tabs":
            self.send_response(404)
            self.end_headers()
            return
        n = int(self.headers.get("Content-Length", 0))
        try:
            tabs = json.loads(self.rfile.read(n) or b"[]")
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return
        with _lock:
            _latest_tabs = tabs
            _last_seen = time.time()
        self.send_response(204)
        self.end_headers()

    def log_message(self, *a):  # ponytail: silence the default stderr access log
        pass


def start_receiver(port=RECEIVER_PORT):
    """Serve the tab receiver on a background daemon thread. Returns the server."""
    srv = ThreadingHTTPServer(("127.0.0.1", port), _TabsHandler)
    threading.Thread(target=srv.serve_forever, daemon=True, name="tab-receiver").start()
    return srv


def _current_tabs():
    with _lock:
        if _latest_tabs is None or time.time() - _last_seen > STALE_SECS:
            return None
        return list(_latest_tabs)


# ---- providers -------------------------------------------------------------
_CHROME_BINS = ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser")


def _find_chrome():
    for b in _CHROME_BINS:
        path = shutil.which(b)
        if path:
            return path
    return None


class ChromeProvider:
    name = "chrome"

    def detect(self):
        tabs = _current_tabs()
        if not tabs:
            return None
        urls = [t["url"] for t in tabs
                if t.get("url", "").startswith(("http://", "https://"))]
        return urls or None

    def restore(self, state):
        chrome = _find_chrome()
        if not chrome or not state:
            return
        subprocess.Popen([chrome, *state])


def _uri_to_path(uri):
    """file:///home/x%20y -> /home/x y. Non-file URIs return None."""
    p = urllib.parse.urlparse(uri)
    if p.scheme != "file":
        return None
    return urllib.parse.unquote(p.path)


def _vscode_folders(storage):
    """Folder paths of the currently-open VS Code windows, from a parsed
    storage.json dict. Unions backupWorkspaces.folders (live = open now) with
    windowsState (last session) and dedupes, so a single open window is caught
    even when openedWindows is empty.
    ponytail: reads VS Code's own state files, not X11 window titles."""
    uris = []
    for f in storage.get("backupWorkspaces", {}).get("folders", []):
        uris.append(f.get("folderUri"))
    ws = storage.get("windowsState", {})
    la = ws.get("lastActiveWindow", {})
    if la.get("folder"):
        uris.append(la["folder"])
    for w in ws.get("openedWindows", []):
        if w.get("folder"):
            uris.append(w["folder"])
    seen, paths = set(), []
    for u in uris:
        path = _uri_to_path(u) if u else None
        if path and path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


class VSCodeProvider:
    name = "vscode"
    STORAGE = "~/.config/Code/User/globalStorage/storage.json"

    def detect(self):
        import os
        try:
            with open(os.path.expanduser(self.STORAGE)) as f:
                folders = _vscode_folders(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        return folders or None

    def restore(self, state):
        if not shutil.which("code") or not state:
            return
        for path in state:
            subprocess.Popen(["code", path])


PROVIDERS = [ChromeProvider(), VSCodeProvider()]


if __name__ == "__main__":
    import http.client

    # 1. receiver round-trips a POST into ChromeProvider.detect()
    srv = start_receiver(port=0)  # ephemeral port, avoids clashing with a live cat
    port = srv.server_address[1]
    payload = json.dumps([
        {"title": "Claude", "url": "https://claude.ai/"},
        {"title": "internal", "url": "chrome://extensions"},  # filtered out
    ])
    c = http.client.HTTPConnection("127.0.0.1", port)
    c.request("POST", "/tabs", body=payload)
    assert c.getresponse().status == 204
    assert ChromeProvider().detect() == ["https://claude.ai/"], "http(s) tabs only"

    # 2. staleness: an old snapshot reads as "Chrome closed" -> None
    with _lock:
        globals()["_last_seen"] = time.time() - STALE_SECS - 1
    assert ChromeProvider().detect() is None, "stale snapshot -> None"

    # 3. VS Code folder extraction from a sample storage.json (no VS Code needed)
    sample = {
        "backupWorkspaces": {"folders": [{"folderUri": "file:///home/eren/a%20b"}]},
        "windowsState": {"lastActiveWindow": {"folder": "file:///home/eren/proj"},
                         "openedWindows": []},
    }
    assert _vscode_folders(sample) == ["/home/eren/a b", "/home/eren/proj"], \
        _vscode_folders(sample)

    srv.shutdown()
    print("OK: tab receiver + chrome filter/staleness + vscode folder parsing")
