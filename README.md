# StickyBisht

A lightweight, customizable(still working) sticky notes application built with Python and Tkinter.

## Project Structure
```
stickybisht/
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
│   └── stickybisht/
│       ├── __init__.py
│       ├── __main__.py
│       └── sticky_notes.py
└── requirements.txt
```

## Installation

```bash
pip install stickybisht
```

## Usage

After installation, you can run the application in two ways:

1. From command line:
```bash
stickybisht
```

2. From Python:
```python
from stickybisht import StickyNote
note = StickyNote()
note.run()
```

## Dependencies
- Python 3.8+
- tkinter (usually comes with Python)

## Development

1. Clone the repository:
```bash
git clone https://github.com/kitparl/stickybisht
cd stickybisht
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install in development mode:
```bash
pip install -e .
```

## License

MIT License
