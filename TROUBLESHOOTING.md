# Troubleshooting Guide

## Common Issues and Solutions

### 1. Mouse Moving to Wrong Screen/Monitor

**Problem**: The mouse moves to the correct coordinates but on the wrong monitor.

**Root Cause**: Monitor offset calculation or monitor selection issues.

**Solutions**:

1. **Verify Monitor Selection**:
   - Check the "Monitor" dropdown in the GUI
   - Ensure you've selected the correct monitor (Primary/Secondary)
   - The status bar will show which monitor is selected and its coordinates

2. **Enable Debug Mode**:
   - Go to Settings tab
   - Enable "Debug Targeting" checkbox
   - Check the console output for coordinate calculations
   - Look for lines like:
     ```
     🎯 Monitor offset: (3008, 991)
     🎯 Target monitor: Secondary
     🎯 Absolute coords: (3908, 1575)
     ```

3. **Check Monitor Information**:
   - The console will show monitor details when you change monitors:
     ```
     📺 Selected monitor Secondary: 1800x1169 at (3008, 991)
     📏 Updated mouse controller monitor offset: (3008, 991)
     ```

4. **Verify Coordinate Calculation**:
   - Monitor 1 (Primary): left=0, top=0 - no offset needed
   - Monitor 2 (Secondary): left=3008, top=991 - offset applied
   - If coordinates seem wrong, check the debug output

### 2. ESC Key Not Working When Other Windows Are Focused

**Problem**: The ESC key only works when the GUI window is focused.

**Root Cause**: This is a limitation of the current hotkey implementation on macOS.

**Solutions**:

1. **Use System Tray Emergency Stop**:
   - Right-click the system tray icon (bottom-right of screen)
   - Select "🚨 Emergency Stop"
   - This works globally regardless of window focus

2. **Keep GUI Window Focused**:
   - Keep the GUI window visible and focused when using mouse control
   - Use a secondary monitor for the GUI while capturing from primary

3. **Use Emergency Stop Button**:
   - Click the red "🚨 EMERGENCY STOP" button in the GUI
   - This is the most reliable method

4. **Alternative Hotkey Methods**:
   - Use macOS System Preferences > Keyboard > Shortcuts
   - Set up a custom keyboard shortcut to activate the emergency stop
   - Use third-party tools like BetterTouchTool for global hotkeys

5. **Terminal Kill Command**:
   - Open Terminal
   - Run: `pkill -f "python.*simple_detector"`
   - This will kill the detection process

### 3. Detection Not Working

**Problem**: No detections are found or detection quality is poor.

**Solutions**:

1. **Check Model Loading**:
   - Ensure the correct model is selected
   - Try different model sizes (n, s, m, l, x)
   - Check console for model loading errors

2. **Verify Screen Capture**:
   - Click "Test Capture" button
   - Ensure screen recording permissions are granted
   - Check that the correct monitor is being captured

3. **Adjust Detection Settings**:
   - Lower confidence threshold in Settings tab
   - Enable debug mode to see detection information
   - Check body part selection checkboxes

4. **Check Lighting and Positioning**:
   - Ensure good lighting for detection
   - Position yourself clearly in the camera view
   - Avoid rapid movements

### 4. Mouse Movement Issues

**Problem**: Mouse movement is jerky, slow, or inaccurate.

**Solutions**:

1. **Adjust Smoothing**:
   - Go to Settings tab
   - Lower the "Smoothing Factor" (0.1-0.3 for smoother movement)
   - Higher values (0.7-1.0) for more responsive movement

2. **Check Confidence Threshold**:
   - Lower the "Target Confidence" in Settings
   - Default is 0.5, try 0.3-0.4 for more sensitive targeting

3. **Enable Debug Mode**:
   - Check console output for movement information
   - Look for distance and duration calculations

4. **Verify Target Parts**:
   - Ensure desired body parts are selected
   - Head and face are highest priority
   - Check that checkboxes are enabled for desired parts

### 5. Performance Issues

**Problem**: Application is slow or laggy.

**Solutions**:

1. **Reduce FPS**:
   - Lower the FPS setting (5-10 FPS is usually sufficient)
   - Higher FPS requires more processing power

2. **Use Smaller Model**:
   - Try yolov8n-pose.pt (fastest)
   - Avoid yolov8x-pose.pt unless needed

3. **Close Other Applications**:
   - Reduce system load
   - Close unnecessary browser tabs and applications

4. **Check System Resources**:
   - Monitor CPU and memory usage
   - Ensure adequate cooling for sustained performance

## Debug Information

### Console Output Examples

**Normal Operation**:
```
📺 Selected monitor Secondary: 1800x1169 at (3008, 991)
📏 Updated mouse controller monitor offset: (3008, 991)
🎯 Detection mode: Custom Selection
🎯 Found 1 detections:
   - head: 0.85
🎯 Targeting head at (3908, 1575) confidence: 0.85
🎯 Processed coords: (320, 240) -> Screen coords: (900, 584)
🎯 Monitor offset: (3008, 991)
🎯 Absolute coords: (3908, 1575)
🎯 Movement: duration=0.045s, distance=125.3px
```

**Error Examples**:
```
❌ Error loading model: [Errno 2] No such file or directory: 'yolov8n-pose.pt'
⚠️ No monitor info available for Secondary
🎯 No detections found for current settings
```

### System Requirements

- **macOS**: 10.14 or later
- **Python**: 3.8 or later
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for models
- **Permissions**: Screen recording access required

### Getting Help

1. **Check Console Output**: Look for error messages and debug information
2. **Enable Debug Mode**: Use Settings tab to enable detailed logging
3. **Test Individual Components**: Use test scripts to isolate issues
4. **Check Permissions**: Ensure screen recording and accessibility permissions
5. **Update Dependencies**: Ensure all packages are up to date

### Emergency Procedures

1. **Immediate Stop**: Use system tray emergency stop or GUI button
2. **Force Quit**: Use Activity Monitor or Terminal to kill the process
3. **Restart Application**: Close and reopen the application
4. **Check Permissions**: Verify screen recording access in System Preferences
5. **Reset Settings**: Use "Reset to Defaults" in Settings tab 