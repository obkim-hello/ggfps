# Installation Guide

## Quick Start

### Basic Installation (Recommended)
```bash
pip install -r requirements.txt
```

### Core Dependencies (Required)
- **PyQt5**: GUI framework
- **opencv-python**: Computer vision and image processing
- **pyautogui**: Mouse and keyboard automation
- **torch**: PyTorch for AI models
- **numpy**: Numerical computing
- **mss**: Screen capture
- **ultralytics**: YOLO models
- **labelImg**: Image annotation tool
- **torchvision**: Computer vision utilities
- **Pillow**: Image processing

### Optional Dependencies

#### keyboard module (for global hotkeys)
```bash
pip install keyboard
```

**Note**: The `keyboard` module is optional and may not work on macOS due to permission restrictions. The application will work without it using GUI-based key detection.

**Benefits with keyboard module**:
- Global hotkeys (F1, F2, ESC) work even when GUI is not focused
- Better cross-platform hotkey support on Windows

**Without keyboard module**:
- ESC key still works when GUI window is focused
- All other functionality remains intact
- More reliable on macOS

## Platform-Specific Notes

### macOS
- **Screen Recording Permission**: Required for screen capture
- **Accessibility Permission**: Required for global hotkeys (if using keyboard module)
- **Recommended**: Install without keyboard module for better compatibility

### Windows
- **No special permissions required** for basic functionality
- **Global hotkeys work** with keyboard module
- **Recommended**: Install with keyboard module for full hotkey support

### Linux
- **May require additional setup** for screen capture
- **Global hotkeys work** with keyboard module
- **Recommended**: Install with keyboard module

## Installation Commands

### Full Installation (with optional dependencies)
```bash
# Install all dependencies including optional ones
pip install -r requirements.txt
```

### Minimal Installation (without optional dependencies)
```bash
# Install core dependencies only
pip install PyQt5 opencv-python pyautogui torch numpy mss ultralytics labelImg torchvision Pillow
```

### Install Optional Dependencies Later
```bash
# Add keyboard module after initial installation
pip install keyboard
```

## Verification

### Test Basic Functionality
```bash
python3 test_stop_functionality.py
```

### Test Full Application
```bash
python3 simple_detector.py
```

### Check Module Availability
```python
# Test if keyboard module is available
try:
    import keyboard
    print("✅ keyboard module available")
except ImportError:
    print("⚠️ keyboard module not available - using GUI-based detection")
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'keyboard'`:
- **Solution**: The application will work without it
- **Alternative**: Install with `pip install keyboard`

### Permission Errors on macOS
If global hotkeys don't work:
- **Solution**: Use ESC key when GUI is focused
- **Alternative**: Grant accessibility permissions to Terminal/IDE

### Screen Capture Issues
If screen capture fails:
- **macOS**: Grant screen recording permission
- **Windows**: Usually works without special setup
- **Linux**: May need additional X11 setup

## Development Setup

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Development Dependencies
```bash
# Additional tools for development
pip install pytest black flake8 mypy
```

## Uninstallation

### Remove All Dependencies
```bash
pip uninstall -r requirements.txt
```

### Remove Specific Module
```bash
pip uninstall keyboard
```

## Support

### Getting Help
- Check the troubleshooting section above
- Review platform-specific notes
- Test with minimal installation first

### Reporting Issues
- Include your platform (macOS/Windows/Linux)
- Specify which dependencies are installed
- Provide error messages and logs 