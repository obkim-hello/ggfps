# GLFPS Solution Summary

## Overview
This project implements a cross-platform Python GUI application for real-time human-like object detection from screen sharing, with customizable I/O actions and training capabilities. The system uses YOLOv5 for detection and provides multiple emergency stop mechanisms.

## Key Features

### 1. Real-time Detection
- **YOLOv5 Integration**: Uses YOLOv5 for fast, accurate object detection
- **Screen Capture**: Cross-platform screen capture with monitor selection
- **Multi-monitor Support**: Handles different monitor configurations
- **Performance Optimization**: Configurable FPS and frame size limits

### 2. Mouse Control System
- **Intelligent Targeting**: Priority-based targeting of body parts (head, face, body, etc.)
- **Smooth Movement**: Configurable smoothing for natural mouse movement
- **Multi-monitor Support**: Correctly handles mouse positioning across monitors
- **Coordinate Scaling**: Properly scales detection coordinates to screen coordinates

### 3. Emergency Stop Mechanisms
- **Multiple Options**: 3 different ways to stop detection
- **Keyboard Hotkeys**: ESC key when GUI is focused
- **Emergency Button**: Always-visible stop button in GUI
- **System Tray**: Global emergency stop via system tray icon

### 4. Training Capabilities
- **Annotation Tools**: Built-in tools for creating training data
- **YOLO Format Support**: Converts between annotation formats
- **Custom Training**: Train models on your own data
- **Data Management**: Organize training datasets

## Installation & Setup

### Prerequisites
```bash
# Python 3.8+ required
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Quick Start
```bash
# Run the application
python3 main.py

# Or use the simple detector
python3 simple_detector.py
```

## Configuration

### Settings Tab
- **Mouse Control**: Smoothing, confidence thresholds, shake sensitivity
- **Performance**: FPS limits, frame size limits
- **Detection**: Confidence thresholds, display options
- **System Info**: Platform, version information

### Detection Modes
- **All Body Parts**: Detect everything with priority ranking
- **Custom Selection**: Choose specific body parts to detect
- **Person Only**: Detect only person class

## Troubleshooting

### Common Issues

#### 1. Mouse on Wrong Screen
**Problem**: Mouse moves to wrong monitor in multi-monitor setup
**Solution**: ✅ FIXED - Added monitor offset calculation and coordinate scaling

#### 2. ESC Key Not Working
**Problem**: Emergency stop hotkey doesn't work when GUI loses focus
**Solution**: ✅ FIXED - Multiple alternatives available:
- Mouse shake detection (works globally)
- Emergency button in GUI
- System tray emergency stop
- Fallback hotkey detection

#### 3. Poor Detection Performance
**Problem**: Low FPS or inaccurate detections
**Solution**: 
- Adjust FPS settings in Settings tab
- Reduce frame size for better performance
- Use appropriate model for your use case
- Ensure good lighting and clear targets

#### 4. macOS Screen Recording Permissions
**Problem**: Can't capture screen on macOS
**Solution**:
- Grant screen recording permissions to Terminal/Python
- System Preferences → Security & Privacy → Privacy → Screen Recording
- Add Terminal.app or your Python IDE

### Debug Mode
Enable debug mode in Settings to see detailed targeting information:
- Detection coordinates
- Mouse movement calculations
- Shake detection events
- Monitor offset calculations

## Testing

### Test Scripts
```bash
# Test mouse shake detection
python3 test_mouse_shake.py

# Test mouse targeting system
python3 test_targeting_system.py

# Test screen capture
python3 test_screen_capture.py

# Demo mouse shake emergency stop
python3 demo_mouse_shake_stop.py
```

### Manual Testing
1. **Mouse Targeting**: Start detection, verify mouse moves to detected objects
2. **Multi-monitor**: Test on different monitors, verify correct positioning
3. **Emergency Stop**: Test all 4 stop methods
4. **Shake Detection**: Shake mouse 3 times, verify detection stops

## File Structure
```
glfps/
├── main.py                 # Main application entry point
├── simple_detector.py      # Simplified detector with GUI
├── glfps/                  # Core modules
│   ├── detection.py        # YOLO detection logic
│   ├── screen_capture.py   # Screen capture utilities
│   ├── gui.py             # GUI components
│   └── automation.py      # Mouse control and automation
├── data/                   # Training data and datasets
├── models/                 # YOLO model files
├── training/               # Training utilities
└── tests/                  # Test scripts and demos
```

## Emergency Stop Methods

### 1. Keyboard ESC
- **How**: Press ESC key
- **When**: Only when GUI window is focused
- **Pros**: Standard, simple
- **Cons**: Focus-dependent, may not work on macOS

### 2. Emergency Button
- **How**: Click red emergency stop button in GUI
- **When**: When GUI is visible
- **Pros**: Always visible, reliable
- **Cons**: Requires GUI to be visible

### 3. System Tray
- **How**: Right-click system tray icon → Emergency Stop
- **When**: Always available
- **Pros**: Global access, always works
- **Cons**: Requires system tray setup

## Performance Tips

### For Better FPS
1. Reduce frame size in Settings
2. Lower FPS setting
3. Use smaller YOLO model
4. Close unnecessary applications
5. Ensure good GPU support

### For Better Accuracy
1. Use appropriate model for your use case
2. Ensure good lighting conditions
3. Adjust confidence thresholds
4. Use custom training data if needed

## Future Enhancements
- [ ] Save/load settings functionality
- [ ] Custom hotkey configuration
- [ ] Advanced targeting algorithms
- [ ] Performance profiling tools
- [ ] Export detection logs
- [ ] Integration with other automation tools

## Support
For issues and questions:
1. Check the troubleshooting section
2. Run test scripts to isolate problems
3. Enable debug mode for detailed logs
4. Check system requirements and permissions 