import os
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, simpledialog

from .ipc import ControlServer
from .platform_compat import (
    apply_linux_wm_env,
    apply_window_attributes,
    context_menu_buttons,
    is_macos,
    modifier,
)

# Path to save sticky note content (kept for back-compat)
SAVE_FILE = Path.home() / ".stickyBishtNotes.txt"

AUTOSAVE_DELAY_MS = 1000
IPC_POLL_MS = 100


def load_note() -> str:
    """Load note content from the save file."""
    if SAVE_FILE.exists():
        return SAVE_FILE.read_text()
    return ""


def save_note(content: str) -> None:
    """Atomically save note content to the save file."""
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(SAVE_FILE.parent),
        prefix=".stickyBishtNotes.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, SAVE_FILE)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


class StickyNote:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stickybisht Note")

        self.bg_color = "#fffa88"
        self.text_color = "black"
        # Helvetica is reliably available to Tk on macOS; Arial elsewhere.
        self.font_style = ("Helvetica", 13) if is_macos() else ("Arial", 12)
        self.alpha = 0.9
        self.default_size = "320x320"
        # Native title bar needs a taller collapsed strip than the Linux custom bar.
        self.collapsed_size = "320x56" if is_macos() else "320x25"
        self._hidden = False
        self._collapsed = False
        self._autosave_after_id = None
        self.title_bar = None

        self.control = ControlServer()

        self.setup_window()
        self.main_frame = tk.Frame(self.root, bg=self.bg_color, highlightthickness=0, bd=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_text_widget()
        self.create_menu()
        self.setup_bindings()
        self._start_ipc()

    def setup_window(self):
        """Configure the main window for the current platform."""
        apply_linux_wm_env()
        apply_window_attributes(self.root, self.alpha)
        self.root.geometry(self.default_size + "+100+100")
        self.root.configure(bg=self.bg_color)
        self.root.minsize(200, 56 if is_macos() else 25)

        # Linux keeps a custom chrome bar (float / drag on Hyprland).
        # macOS uses the native title bar only — avoids double chrome.
        if is_macos():
            return

        self.title_bar = tk.Frame(self.root, bg="#2e2e2e", height=25)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)

        title_label = tk.Label(
            self.title_bar, text="Stickybisht Note", bg="#2e2e2e", fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=5)

        self.hide_button = tk.Button(
            self.title_bar,
            text="-",
            command=self.toggle_collapse,
            bg="#2e2e2e",
            fg="white",
            bd=0,
            padx=5,
            highlightthickness=0,
        )
        self.hide_button.pack(side=tk.RIGHT)

        self.close_button = tk.Button(
            self.title_bar,
            text="×",
            command=self.hide,
            bg="#2e2e2e",
            fg="white",
            bd=0,
            padx=5,
            highlightthickness=0,
        )
        self.close_button.pack(side=tk.RIGHT)

        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        self.title_bar.bind("<Double-Button-1>", lambda e: self.toggle_collapse())
        title_label.bind("<Double-Button-1>", lambda e: self.toggle_collapse())

    def create_text_widget(self):
        """Create a full-bleed note surface with an auto-hiding scrollbar."""
        self.text_frame = tk.Frame(
            self.main_frame, bg=self.bg_color, highlightthickness=0, bd=0
        )
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)

        self.v_scrollbar = tk.Scrollbar(
            self.text_frame,
            width=8,
            troughcolor=self.bg_color,
            bg="#d4c86a",
            activebackground="#c4b85a",
            highlightthickness=0,
            bd=0,
        )

        self.text = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=self.font_style,
            bg=self.bg_color,
            fg=self.text_color,
            padx=12,
            pady=12,
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT,
            yscrollcommand=self._on_text_scroll,
            insertbackground=self.text_color,
            undo=True,
        )
        self.text.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.config(command=self.text.yview)

        saved_content = load_note()
        if saved_content:
            self.text.insert("1.0", saved_content)
        self.text.edit_modified(False)

    def _on_text_scroll(self, first, last):
        """Show the vertical scrollbar only when content overflows."""
        self.v_scrollbar.set(first, last)
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.v_scrollbar.grid_remove()
        else:
            self.v_scrollbar.grid(row=0, column=1, sticky="ns")

    def create_menu(self):
        """Create the right-click menu."""
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Change Background Color", command=self.set_bg_color)
        self.menu.add_command(label="Change Text Color", command=self.set_text_color)
        self.menu.add_command(label="Change Font", command=self.set_font)
        self.menu.add_command(label="Set Transparency", command=self.set_transparency)
        self.menu.add_separator()
        self.menu.add_command(label="Save", command=self.save_now)
        self.menu.add_command(label="Collapse / Expand", command=self.toggle_collapse)
        self.menu.add_command(label="Hide", command=self.hide)
        self.menu.add_command(label="Exit", command=self.quit)

    def setup_bindings(self):
        """Set up mouse and keyboard bindings."""
        for sequence in context_menu_buttons():
            self.text.bind(sequence, self.show_menu)
            self.root.bind(sequence, self.show_menu)

        mod = modifier()
        self.root.bind(f"<{mod}-s>", lambda e: self.save_now())
        self.root.bind(f"<{mod}-h>", lambda e: self.toggle_collapse())
        # Keep Control bindings available on macOS for muscle memory / Linux habits
        if is_macos():
            self.root.bind("<Control-s>", lambda e: self.save_now())
            self.root.bind("<Control-h>", lambda e: self.toggle_collapse())

        # Close / red traffic light hides; Exit menu / stickybisht quit ends the process
        self.root.protocol("WM_DELETE_WINDOW", self.hide)

        self.text.bind("<FocusIn>", lambda e: self.text.configure(insertbackground=self.text_color))
        self.text.bind("<FocusOut>", lambda e: self.text.configure(insertbackground=self.text_color))
        self.text.bind("<<Modified>>", self._on_text_modified)

    def _start_ipc(self) -> None:
        if not self.control.start():
            # Another instance owns the socket; this process should not keep running.
            # The CLI normally prevents this path, but be defensive if StickyNote is
            # constructed directly.
            self.root.destroy()
            raise RuntimeError("Another StickyBisht instance is already running")
        self._poll_ipc()

    def _poll_ipc(self) -> None:
        self.control.drain(self._handle_ipc_command)
        self.root.after(IPC_POLL_MS, self._poll_ipc)

    def _handle_ipc_command(self, command: str) -> None:
        if command == "show":
            self.show()
        elif command == "hide":
            self.hide()
        elif command == "toggle":
            self.toggle_visibility()
        elif command == "quit":
            self.quit()

    def start_drag(self, event):
        """Begin window drag."""
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        """Handle window dragging."""
        x = self.root.winfo_pointerx() - self.x
        y = self.root.winfo_pointery() - self.y
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        """Show the right-click menu."""
        self.menu.tk_popup(event.x_root, event.y_root)

    def current_content(self) -> str:
        return self.text.get("1.0", tk.END).strip()

    def save_now(self, event=None) -> None:
        """Save immediately and clear any pending autosave."""
        if self._autosave_after_id is not None:
            self.root.after_cancel(self._autosave_after_id)
            self._autosave_after_id = None
        save_note(self.current_content())
        self.text.edit_modified(False)

    def _on_text_modified(self, event=None) -> None:
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        if self._autosave_after_id is not None:
            self.root.after_cancel(self._autosave_after_id)
        self._autosave_after_id = self.root.after(AUTOSAVE_DELAY_MS, self._autosave)

    def _autosave(self) -> None:
        self._autosave_after_id = None
        save_note(self.current_content())

    def show(self) -> None:
        """Bring the note to the front and focus the text area."""
        self._hidden = False
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.text.focus_set()

    def hide(self) -> None:
        """Hide the window without quitting; persist content first."""
        self.save_now()
        self._hidden = True
        self.root.withdraw()

    def toggle_visibility(self) -> None:
        """Toggle between fully hidden and shown (used by global hotkey)."""
        if self._hidden or not self.root.winfo_viewable():
            self.show()
        else:
            self.hide()

    def toggle_collapse(self) -> None:
        """Toggle between full size and the compact strip."""
        if self._hidden:
            self.show()
            return
        if self._collapsed:
            self.root.geometry(self.default_size)
            self._collapsed = False
        else:
            self.root.geometry(self.collapsed_size)
            self._collapsed = True

    def set_bg_color(self):
        """Change background color."""
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.bg_color = color
            self.root.configure(bg=self.bg_color)
            self.text.config(bg=self.bg_color)
            self.main_frame.config(bg=self.bg_color)
            self.text_frame.config(bg=self.bg_color)
            self.v_scrollbar.config(troughcolor=self.bg_color)

    def set_text_color(self):
        """Change text color."""
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            self.text_color = color
            self.text.config(fg=self.text_color, insertbackground=self.text_color)

    def set_font(self):
        """Change font style and size."""
        font_name = simpledialog.askstring(
            "Font",
            "Enter font name (e.g., Arial):",
            initialvalue=self.font_style[0],
        )
        font_size = simpledialog.askinteger(
            "Font Size",
            "Enter font size:",
            initialvalue=self.font_style[1],
        )
        if font_name and font_size:
            self.font_style = (font_name, font_size)
            self.text.config(font=self.font_style)

    def set_transparency(self):
        """Change window transparency."""
        new_alpha = simpledialog.askfloat(
            "Transparency",
            "Enter transparency (0.1 to 1):",
            initialvalue=self.alpha,
        )
        if new_alpha and 0.1 <= new_alpha <= 1.0:
            self.alpha = new_alpha
            self.root.attributes("-alpha", self.alpha)

    def quit(self) -> None:
        """Save content, stop IPC, and close the application."""
        self.save_now()
        self.control.stop()
        self.root.destroy()

    def run(self):
        """Start the application."""
        self.text.focus_set()
        self.root.mainloop()


if __name__ == "__main__":
    note = StickyNote()
    note.run()
