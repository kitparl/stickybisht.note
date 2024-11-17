import tkinter as tk
from tkinter import colorchooser, simpledialog, font
from pathlib import Path
import os

# Path to save sticky note content
SAVE_FILE = Path.home() / ".stickyBishtNotes.txt"

def load_note():
    """Load note content from the save file."""
    if SAVE_FILE.exists():
        return SAVE_FILE.read_text()
    return ""

def save_note(content):
    """Save note content to the save file."""
    SAVE_FILE.write_text(content)

class StickyNote:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stickybisht Note")

        # Default settings
        self.bg_color = "#fffa88"
        self.text_color = "black"
        self.font_style = ("Arial", 12)
        self.alpha = 0.9
        self.default_size = "300x300"  # Store default size

        # Configure window for Hyprland
        self.setup_window()

        # Create main frame with proper weight configuration
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create text widget
        self.create_text_widget()

        # Create menu
        self.create_menu()

        # Set up bindings
        self.setup_bindings()

    def setup_window(self):
        """Configure the main window for Hyprland."""
        # Make window floating in Hyprland
        os.environ['_JAVA_AWT_WM_NONREPARENTING'] = '1'

        # Set window properties
        self.root.attributes('-type', 'dialog')
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', self.alpha)

        # Set initial geometry
        self.root.geometry(self.default_size + "+100+100")

        # Add a title bar
        self.title_bar = tk.Frame(self.root, bg='#2e2e2e', height=25)
        self.title_bar.pack(fill=tk.X)

        # Add title label
        title_label = tk.Label(self.title_bar, text="Stickybisht Note", bg='#2e2e2e', fg='white')
        title_label.pack(side=tk.LEFT, padx=5)

        # Add hide button (instead of minimize)
        self.hide_button = tk.Button(self.title_bar, text='-', command=self.toggle_visibility,
                                   bg='#2e2e2e', fg='white', bd=0, padx=5)
        self.hide_button.pack(side=tk.RIGHT)

        # Add close button
        self.close_button = tk.Button(self.title_bar, text='×', command=self.save_and_exit,
                                    bg='#2e2e2e', fg='white', bd=0, padx=5)
        self.close_button.pack(side=tk.RIGHT)

        # Bind dragging to title bar
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        
        # Bind double-click to title bar and title label
        self.title_bar.bind("<Double-Button-1>", lambda e: self.toggle_visibility())
        title_label.bind("<Double-Button-1>", lambda e: self.toggle_visibility())

    def create_text_widget(self):
        """Create and configure the text widget."""
        # Create text widget with scrollbar
        self.text_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for text_frame
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)

        # Create vertical scrollbar
        self.v_scrollbar = tk.Scrollbar(self.text_frame, width=7)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        self.h_scrollbar = tk.Scrollbar(self.text_frame, orient=tk.HORIZONTAL, width=7)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create text widget with both scrollbars
        self.text = tk.Text(self.text_frame, 
                           wrap=tk.NONE,  # Changed to NONE to allow horizontal scrolling
                           font=self.font_style,
                           bg=self.bg_color, 
                           fg=self.text_color,
                           padx=10, 
                           pady=10,
                           yscrollcommand=self.v_scrollbar.set,
                           xscrollcommand=self.h_scrollbar.set,
                           insertbackground=self.text_color)

        # Pack text widget
        self.text.pack(fill=tk.BOTH, expand=True)

        # Configure scrollbars
        self.v_scrollbar.config(command=self.text.yview)
        self.h_scrollbar.config(command=self.text.xview)

        # Insert any saved content
        saved_content = load_note()
        if saved_content:
            self.text.insert("1.0", saved_content)

    def create_menu(self):
        """Create the right-click menu."""
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Change Background Color", command=self.set_bg_color)
        self.menu.add_command(label="Change Text Color", command=self.set_text_color)
        self.menu.add_command(label="Change Font", command=self.set_font)
        self.menu.add_command(label="Set Transparency", command=self.set_transparency)
        self.menu.add_separator()
        self.menu.add_command(label="Save", command=lambda: save_note(self.text.get("1.0", tk.END).strip()))
        self.menu.add_command(label="Exit", command=self.save_and_exit)

    def setup_bindings(self):
        """Set up mouse and keyboard bindings."""
        # Bind right-click menu
        self.text.bind("<Button-3>", self.show_menu)
        self.root.bind("<Button-3>", self.show_menu)

        # Bind keyboard shortcuts
        self.root.bind("<Control-s>", lambda e: save_note(self.text.get("1.0", tk.END).strip()))
        self.root.bind("<Control-h>", lambda e: self.toggle_visibility())

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.save_and_exit)

        # Bind focus events
        self.text.bind("<FocusIn>", lambda e: self.text.configure(insertbackground=self.text_color))
        self.text.bind("<FocusOut>", lambda e: self.text.configure(insertbackground=self.text_color))

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

    def toggle_visibility(self):
        """Toggle window visibility between minimized and default size."""
        current_geometry = self.root.geometry().split('+')[0]  # Get current size without position
        if current_geometry == "300x25":  # If minimized
            self.root.geometry(self.default_size)  # Restore to default size
        else:
            self.root.geometry("300x25")  # Minimize

    def set_bg_color(self):
        """Change background color."""
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.bg_color = color
            self.text.config(bg=self.bg_color)
            self.main_frame.config(bg=self.bg_color)
            self.text_frame.config(bg=self.bg_color)

    def set_text_color(self):
        """Change text color."""
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            self.text_color = color
            self.text.config(fg=self.text_color, insertbackground=self.text_color)

    def set_font(self):
        """Change font style and size."""
        font_name = simpledialog.askstring("Font", "Enter font name (e.g., Arial):",
                                         initialvalue=self.font_style[0])
        font_size = simpledialog.askinteger("Font Size", "Enter font size:",
                                          initialvalue=self.font_style[1])
        if font_name and font_size:
            self.font_style = (font_name, font_size)
            self.text.config(font=self.font_style)

    def set_transparency(self):
        """Change window transparency."""
        new_alpha = simpledialog.askfloat("Transparency", "Enter transparency (0.1 to 1):",
                                        initialvalue=self.alpha)
        if new_alpha and 0.1 <= new_alpha <= 1.0:
            self.alpha = new_alpha
            self.root.attributes('-alpha', self.alpha)

    def update_scrollbars(self):
        """Update scrollbar visibility based on content."""
        # Get text widget dimensions and content size
        text_width = self.text.winfo_width()
        text_height = self.text.winfo_height()
        content_width = self.text.bbox("end-1c")[0] + 50 if self.text.bbox("end-1c") else 0
        content_height = self.text.bbox("end-1c")[1] + 50 if self.text.bbox("end-1c") else 0

        # Show/hide vertical scrollbar
        if content_height > text_height:
            self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.v_scrollbar.pack_forget()

        # Show/hide horizontal scrollbar
        if content_width > text_width:
            self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.h_scrollbar.pack_forget()

    def save_and_exit(self):
        """Save content and close the application."""
        save_note(self.text.get("1.0", tk.END).strip())
        self.root.destroy()

    def run(self):
        """Start the application."""
        # Focus on the text widget
        self.text.focus_set()
        self.root.mainloop()

if __name__ == "__main__":
    note = StickyNote()
    note.run()
