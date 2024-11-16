# StickyBisht Note

A customizable sticky notes application for Linux and Windows desktop environments.

## Project Structure
```
stickybisht.note/
├── LICENSE
├── README.md
├── pyproject.toml
├── setup.cfg
├── src/
│   └── stickybisht/
│       ├── __init__.py
│       ├── __main__.py
│       ├── sticky_notes.py
│       └── resources/
│           └── icons/
│               └── sticky.png
├── scripts/
│   ├── stickybisht
│   └── stickybisht.bat
├── .gitignore
└── requirements.txt
```

## Installation Methods

### From PyPI (All Platforms)
```bash
pip install stickybisht-note
```

### Linux Package Managers

#### Fedora
```bash
sudo dnf install python3-tkinter
sudo dnf install stickybisht-note
```

#### Ubuntu
```bash
sudo apt install python3-tk
sudo apt install stickybisht-note
```

#### Arch Linux
```bash
sudo pacman -S python-tk
yay -S stickybisht-note
```

### Windows
1. Download the latest release from GitHub Releases
2. Run the installer (.exe)
3. Launch from Start Menu

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/kitparl/stickybisht.note
cd stickybisht.note
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Dependencies
- Python 3.8+
- tkinter
- pathlib

## Building from Source

### Linux/macOS
```bash
python -m build
```

### Windows
```bash
python -m build
```

## Running Tests
```bash
pytest tests/
```
