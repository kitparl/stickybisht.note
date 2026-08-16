"""Entry point for StickyBisht."""

from __future__ import annotations

import argparse
import subprocess
import sys


def _spawn_detached() -> None:
    """Start StickyBisht in a new session so the CLI can exit immediately."""
    subprocess.Popen(
        [sys.executable, "-m", "stickybisht", "run"],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _run_app() -> int:
    try:
        import tkinter as tk  # noqa: F401
    except Exception:
        print("Error: Tkinter is not properly installed.", file=sys.stderr)
        print("Please install python3-tk package for your system:", file=sys.stderr)
        print("  Fedora: sudo dnf install python3-tk", file=sys.stderr)
        print("  Ubuntu: sudo apt install python3-tk", file=sys.stderr)
        print("  Arch: sudo pacman -S tk", file=sys.stderr)
        print("  macOS: use a Python build that includes Tk (python.org or Homebrew python-tk)", file=sys.stderr)
        return 1

    from .platform_compat import macos_system_tk_is_unsafe

    unsafe = macos_system_tk_is_unsafe()
    if unsafe:
        print(f"Error: {unsafe}", file=sys.stderr)
        print(f"Python: {sys.executable}", file=sys.stderr)
        return 1

    from .stickybisht_notes import StickyNote

    try:
        note = StickyNote()
        note.run()
    except RuntimeError as e:
        print(f"Error starting StickyBisht: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error starting StickyBisht: {e}", file=sys.stderr)
        return 1
    return 0


def _send_or_spawn(command: str) -> int:
    from .ipc import send_command

    response = send_command(command)
    if response is not None:
        return 0

    if command in ("show", "toggle"):
        _spawn_detached()
        return 0

    print("StickyBisht is not running.", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stickybisht",
        description="Lightweight sticky note with OS-level hotkey control.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=("run", "toggle", "show", "hide", "quit"),
        help="run (default): start or focus; toggle/show/hide/quit: control a running instance",
    )

    args = parser.parse_args(argv)
    command = args.command

    if command == "run":
        from .ipc import is_server_running, send_command

        if is_server_running():
            send_command("show")
            return 0
        return _run_app()

    return _send_or_spawn(command)


if __name__ == "__main__":
    sys.exit(main())
