# catyhoo tab capture extension

One-time setup so the cat can save/restore your open Chrome tabs. Chrome ≥136
ignores `--remote-debugging-port` on your real profile (a security change), so
this small extension pushes the tab list to the running cat instead.

**Install once:** open `chrome://extensions`, turn on **Developer mode**
(top-right), click **Load unpacked**, and pick this `extension/` folder.

That's it. From then on, while catyhoo is running, your open tabs are captured
automatically — `/workspace save <name>` records them, `/workspace run <name>`
reopens them. Nothing to launch with flags, no per-session steps.
