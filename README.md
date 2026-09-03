# Elden Ring Mod Manager

A lightweight Python GUI application for managing and switching between multiple Elden Ring mod profiles.

Elden Ring Mod Switcher allows you to maintain separate mod setups without duplicating your entire game installation. Profiles store only the modified files, and the application handles copying, deleting, and restoring files when switching between profiles.

## Requirements

- Python 3.10+
- PySide6

# Installation

### Clone the repository
```bash
git clone https://github.com/yourusername/EldenRing-ModSwitcher.git
```

### Activate virtual environment

Linux/MacOS:
```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```
### Run
```bash
python main.py
```

## Build

Install PyInstaller and build a windowed executable for the current platform:

```bash
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --name EldenRing-ModManager main.py
```

The executable is created in `dist/EldenRing-ModManager`. GitHub Actions builds
Linux and Windows artifacts when a `v*` tag is pushed or when the workflow is
started manually.
