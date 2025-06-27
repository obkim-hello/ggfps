# Packaging Guide

## 1. Prerequisites
- Python 3.x installed
- All dependencies installed (see `requirements.txt`)
- For macOS: Xcode Command Line Tools
- For Windows: Visual Studio Build Tools (if needed)

## 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. Packaging with PyInstaller
Install PyInstaller:
```bash
pip install pyinstaller
```

### macOS
```bash
pyinstaller --onefile --windowed main.py
```
- The app bundle will be in the `dist/` folder.

### Windows
```bash
pyinstaller --onefile --windowed main.py
```
- The `.exe` will be in the `dist\` folder.

## 4. Additional Notes
- For GUI apps, use the `--windowed` flag to avoid opening a terminal window.
- You may need to adjust the PyInstaller spec file for data files or model weights.
- Test the packaged app on a clean system.

See `README.md` for an overview. 