## [0.2.0] - 2026-08-07
### Added
- macOS support (skip X11-only window attributes that crashed on Mac)
- Single-instance control via Unix socket (`stickybisht toggle|show|hide|quit`)
- Debounced autosave and atomic writes to `~/.stickyBishtNotes.txt`
- Native macOS title bar; custom chrome kept on Linux
- Docs for Hammerspoon / Hyprland global hotkeys

### Changed
- Close / traffic-light hides the note; Exit or `stickybisht quit` ends the process
- Platform-aware shortcuts (Command on macOS, Control on Linux)

## [0.1.1] - 2024-11-17
### Added
- New feature: Double click toggle minimise and default size

### Fixed
- Border scrollable thickness
