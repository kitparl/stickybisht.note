"""Platform-specific helpers for StickyBisht (macOS vs Linux)."""

from __future__ import annotations

import sys


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def modifier() -> str:
    """Return the primary accelerator key name for Tk bindings."""
    return "Command" if is_macos() else "Control"


def context_menu_buttons() -> tuple[str, ...]:
    """
    Button sequences that should open the context menu.

    On macOS, Tk/Aqua typically does not deliver Button-3 for a right-click;
    Button-2 and Control-Button-1 are the reliable alternatives.
    """
    if is_macos():
        return ("<Button-2>", "<Control-Button-1>")
    return ("<Button-3>",)


def apply_linux_wm_env() -> None:
    """Set env vars that help floating windows under X11/Hyprland."""
    if is_linux():
        import os

        os.environ.setdefault("_JAVA_AWT_WM_NONREPARENTING", "1")


def apply_window_attributes(root, alpha: float) -> None:
    """
    Apply shared and platform-specific Tk window attributes.

    attributes('-type', ...) is X11-only and crashes on macOS.
    """
    if is_linux():
        root.attributes("-type", "dialog")
    root.attributes("-topmost", True)
    root.attributes("-alpha", alpha)
