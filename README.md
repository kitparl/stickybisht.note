# StickyBisht

A lightweight, customizable sticky notes application built with Python and Tkinter.
Runs on **macOS** and **Linux** (including Hyprland via XWayland). Designed for quick capture while you work: one note, always available via a system hotkey.

## Features

- Single sticky note that stays out of the way (hide or collapse)
- Content persisted to `~/.stickyBishtNotes.txt` (atomic writes + debounced autosave)
- Always-on-top, adjustable transparency, colors, and font via right-click menu
- OS-level control via CLI (`stickybisht toggle`) so you can bind a global hotkey without Accessibility permissions for StickyBisht itself
- Platform-aware shortcuts: **Command** on macOS, **Control** on Linux
- Native macOS title bar; custom compact chrome on Linux

## Installation

```bash
pip install stickybisht
```

Or from source (recommended for development):

```bash
cd stickybisht.note
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Requires Python 3.8+ with a working Tkinter. On macOS, prefer Homebrew Python with Tk (`brew install python-tk@3.12`) or the [python.org](https://www.python.org/downloads/) installer — Apple’s system Python often ships a broken Tk.

## Usage

### CLI

| Command | Effect |
| --- | --- |
| `stickybisht` / `stickybisht run` | Start the note, or show/focus it if already running |
| `stickybisht toggle` | Show if hidden, hide if visible (starts the app if needed) |
| `stickybisht show` | Show and focus (starts if needed) |
| `stickybisht hide` | Hide without quitting |
| `stickybisht quit` | Save and exit the running instance |

On macOS, the red traffic-light close button **hides** the note (process keeps running). Use the right-click **Exit** menu item or `stickybisht quit` to fully quit. On Linux, the custom `×` does the same hide; `-` collapses.

If `stickybisht` aborts on macOS but `python -c "import tkinter; tkinter.Tk().destroy()"` works, try `python -m stickybisht` instead.

### In-app shortcuts

| Action | macOS | Linux |
| --- | --- | --- |
| Save | `Cmd+S` (also `Ctrl+S`) | `Ctrl+S` |
| Collapse / expand | `Cmd+H` (also `Ctrl+H`) | `Ctrl+H` |
| Context menu | Right-click / Ctrl-click | Right-click |

Collapse stays on screen as a thin strip; hide withdraws the window entirely. Both are available from the context menu.

### Global hotkeys

StickyBisht does **not** grab keys itself. Bind your OS to run `stickybisht toggle` (or `python -m stickybisht toggle`).

Suggested defaults: **`Cmd+Opt+N`** on macOS, **`Super+N`** on Linux.

#### macOS — Hammerspoon (recommended)

1. **Install Hammerspoon**

   ```bash
   brew install --cask hammerspoon
   ```

   Or download from [hammerspoon.org](https://www.hammerspoon.org).

2. **Open Hammerspoon once** and allow **Accessibility** when prompted  
   (System Settings → Privacy & Security → Accessibility → enable Hammerspoon).  
   Hotkeys will not fire without this.

3. **Edit the config** — Hammerspoon menu bar icon → **Open Config**  
   (creates `~/.hammerspoon/init.lua` if needed). Add:

   ```lua
   -- StickyBisht: Cmd+Opt+N toggles the note
   -- Prefer an absolute path so Hammerspoon does not pick the wrong Python.
   local sticky = "/Users/YOUR_USER/Documents/personal-work/stickybisht.note/.venv/bin/python -m stickybisht"

   hs.hotkey.bind({"cmd", "alt"}, "N", function()
     hs.execute(sticky .. " toggle", true)
   end)

   -- Optional: Cmd+Opt+Shift+N quits
   hs.hotkey.bind({"cmd", "alt", "shift"}, "N", function()
     hs.execute(sticky .. " quit", true)
   end)
   ```

   Replace `YOUR_USER` / the path with your real project `.venv`.  
   If you installed globally and `which stickybisht` is correct for GUI apps, you can use `hs.execute("stickybisht toggle", true)` instead.

4. **Reload** — Hammerspoon menu → **Reload Config**.

5. Press **`Cmd+Opt+N`** from any app. The note should show or hide.

If nothing happens: confirm Accessibility is on, and run the same shell command in Terminal to verify the path.

**skhd** alternative:

```
cmd + alt - n : /path/to/.venv/bin/python -m stickybisht toggle
```

#### macOS — Automator (no extra install)

1. Automator → Quick Action → “Workflow receives **no input** in **any application**”
2. Add **Run Shell Script** with your full command, e.g.  
   `/path/to/.venv/bin/python -m stickybisht toggle`
3. System Settings → Keyboard → Keyboard Shortcuts → Services → assign a key

Automator Services can be laggy or miss presses; prefer Hammerspoon when possible.

#### Hyprland

In `hyprland.conf`:

```
bind = SUPER, N, exec, stickybisht toggle
```

Optional float rule if the dialog window type is not enough:

```
windowrulev2 = float, class:^(stickybisht)$
```

### From Python

```python
from stickybisht import StickyNote
note = StickyNote()
note.run()
```

## How control works

A running instance listens on a Unix socket at `~/.stickybisht/ctl.sock`. CLI commands connect and send `show` / `hide` / `toggle` / `quit`. If nothing is listening, `toggle` and `show` start a detached instance.

## Project structure

```
stickybisht/
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
│   └── stickybisht/
│       ├── __init__.py
│       ├── __main__.py          # CLI
│       ├── stickybisht_notes.py # Tk UI
│       ├── platform_compat.py   # macOS / Linux window & key helpers
│       └── ipc.py               # single-instance control socket
└── requirements.txt
```

## Development

```bash
git clone https://github.com/kitparl/stickybisht
cd stickybisht
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
python -m stickybisht
```

## Notes and limitations

- On macOS, if the note appears after a hotkey but keystrokes still go to the previous app, click the note once; a future `.app` bundle will activate via LaunchServices more cleanly.
- Some Homebrew Tk builds abort with `macOS 15 (1507) required…` on slightly older 15.x builds — update macOS or use the python.org installer.
- Under Wayland (e.g. Hyprland), Tk runs via XWayland; positioning and always-on-top depend on the compositor.
- One note per user session (single instance). Multiple notes are a later enhancement.

## Contributing

Contributions are welcome. Please open an issue first for larger changes.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your_username/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/your_username/AmazingFeature`)
5. Open a Pull Request

## License

MIT License
