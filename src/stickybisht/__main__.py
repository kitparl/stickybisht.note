import sys
import tkinter as tk
from .stickybisht_notes import StickyNote

def main():
    """Entry point for the application."""
    try:
        # Check if tkinter is available
        if not sys.modules.get('tkinter'):
            tk.Tk()
    except Exception as e:
        print("Error: Tkinter is not properly installed.", file=sys.stderr)
        print("Please install python3-tk package for your system:", file=sys.stderr)
        print("  Fedora: sudo dnf install python3-tk", file=sys.stderr)
        print("  Ubuntu: sudo apt install python3-tk", file=sys.stderr)
        print("  Arch: sudo pacman -S tk", file=sys.stderr)
        sys.exit(1)

    try:
        note = StickyNote()
        note.run()
    except Exception as e:
        print(f"Error starting StickyBisht: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
