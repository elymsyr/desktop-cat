# Roadmap

`catyhoo` is the cross-platform (PySide6) desktop cat. The visual shell —
animated cat, drag, tray, prompt box, help book — already ships. From here the
work is the two features in [FEATURES.md](FEATURES.md): **MCP integration** and
**Workspace management**, built incrementally, Linux-first, OS-agnostic tools.

Methodology: step-by-step. Each phase is reviewed and approved before the next.

## Testing the MCP layer — free LLM options

| Tool | Free quota | Tool-calling | Role |
|------|-----------|--------------|------|
| **MCP Inspector** (`npx @modelcontextprotocol/inspector`) | local, unlimited | — | Test the server directly, no LLM. **Use first.** |
| **Google Gemini** (2.0 Flash) | ~15 RPM / ~1500 per day | yes, mature | Primary LLM-driven E2E. Single API key. |
| **Groq** (Llama 3.x) | generous, fastest | yes (OpenAI-compatible) | Speed-focused fallback; bridge MCP↔tools. |
| **Claude Desktop / Code** | plan-based | yes | Native MCP client for real-client validation. |

**Recommendation:** develop against MCP Inspector, run LLM-driven E2E with
Gemini (Groq as a fast fallback), validate native-client behaviour with Claude.

## Phases

### Phase 0 — Foundation
- [ ] `config.py`: single JSON file (`json`), `load` / `save` / live `reload`.
- [ ] Replace the echo in `prompt.py` with an `alias -> function` dispatch map.
- **Verify:** `/help` prints into the book; unknown command is reported.

### Phase 1 — Local tools (prompt only, no MCP yet)
- [ ] `tools.py`: `notify(msg)` via tray `QSystemTrayIcon.showMessage`.
- [ ] `time_event(when, msg)`: one-shot/relative `QTimer` that fires `notify`.
- **Verify:** `/notify hi` shows a desktop notification; `/time-event 5s hi` fires.

### Phase 2 — MCP server
- [ ] Add `mcp` (FastMCP) to `requirements.txt`.
- [ ] `mcp_server.py`: asyncio server on one background thread, Streamable-HTTP/SSE
      on a local port; GUI-touching calls marshalled to the Qt main thread via a
      queued signal.
- [ ] Register `notify` / `time_event` as MCP tools (same functions as Phase 1).
- **Verify:** MCP Inspector lists & calls the tools; then one Gemini tool-call round-trip.

### Phase 3 — Persistence
- [ ] `reminder(when, msg)`: like `time_event` but persisted, survives restart.
- [ ] Live config reload wired in.
- **Verify:** set a reminder, restart the cat, reminder still fires.

### Phase 4 — Workspace providers
- [ ] Provider contract: `name`, `detect() -> state | None`, `restore(state)`
      (plain `Protocol` + a list, no registry).
- [x] `ChromeProvider`: detect tabs via a one-time MV3 extension that pushes
      `chrome.tabs.query` to a local `http.server` receiver (CDP `--remote-debugging-port`
      is ignored by Chrome ≥136 on the real profile); restore launches Chrome with saved URLs.
- [x] `VSCodeProvider`: detect open folders from `storage.json` workspace state; restore `code <path>`.
- [x] Commands `/workspace save|list|run <name>`.
- **Verify:** load `extension/` once, `save`, close Chrome, `run` → tabs reopen.

### Phase 5 — Workspace over MCP
- [x] Register the workspace operations as MCP tools too.
- **Verify:** an external client (Inspector/Gemini/Claude) saves & restores a workspace.
  Done — `e2e_llm.py`: a free Gemini, given plain English, discovers the tools and
  calls `workspace_save`/`workspace_list` itself (`GEMINI_API_KEY=... python e2e_llm.py`).

### Phase 6 — Cross-platform & packaging (later)
- [ ] macOS / Windows provider variants behind the same contract.
- [ ] Packaging.

## Principles
- No speculative abstraction: `Protocol` + list, stdlib `json` / `urllib` / `asyncio`,
  one background thread.
- One function = one MCP tool = one `/command` (FastMCP), no per-tool plumbing.
- Each logic module carries one `__main__` self-check (see `cat.py`'s `_flat_line`).
