# Mouse Targeting System

## Overview
The application now features an intelligent mouse targeting system that automatically moves the mouse to the center of detected human body parts based on a configurable priority ranking system. The system includes coordinate scaling to ensure accurate targeting.

## Priority Ranking System

### Body Part Priority (Highest to Lowest)
1. **Head** (Priority 1) - Highest priority target
2. **Face** (Priority 2) - Second highest priority
3. **Torso** (Priority 3) - Body center
4. **Body** (Priority 4) - Full body outline
5. **Left Leg** (Priority 5) - Left leg region
6. **Right Leg** (Priority 5) - Right leg region
7. **Left Arm** (Priority 6) - Left arm region
8. **Right Arm** (Priority 6) - Right arm region
9. **Left Hand** (Priority 7) - Left hand
10. **Right Hand** (Priority 7) - Right hand
11. **Left Foot** (Priority 8) - Left foot
12. **Right Foot** (Priority 8) - Right foot
13. **Person** (Priority 9) - Full person (lowest priority)

### Targeting Logic

The mouse targeting system now respects your body part selection:

```python
# Mouse only considers detections from selected body parts
if label in self.body_part_priority and self.body_part_priority[label] < 999:
    # Among selected parts, target highest confidence
    if confidence > best_confidence and confidence > confidence_threshold:
        best_target = detection
```

**Key Features:**
- **User Selection**: Only targets body parts you've checked
- **Confidence Based**: Among selected parts, targets highest confidence
- **Real-time**: Changes apply immediately when checkboxes change
- **No Fixed Priority**: No hardcoded priority system

## Key Features

### Center Targeting
- Mouse moves to the exact center of detected bounding boxes
- Calculated as: `center_x = x + width // 2`, `center_y = y + height // 2`
- Ensures precise targeting regardless of bounding box size

### Confidence Filtering
- Only targets detections above the confidence threshold
- Configurable threshold (30-90%)
- Prevents targeting low-confidence detections

### Smooth Movement
- Natural mouse movement with configurable smoothing
- Smoothing factor: 10-90% (higher = smoother)
- Prevents jerky mouse movements

### Debug Mode
- Console output shows targeting information
- Displays: target body part, coordinates, confidence
- Helps understand targeting decisions

### Coordinate Scaling
- **NEW: Fixed Coordinate Scaling** - The system now properly scales coordinates from the processed detection frame to the original screen coordinates, ensuring the mouse points to the exact center of bounding boxes.
- **Automatic Scaling**: Coordinates are automatically scaled from processed frame to screen
- **Performance Optimized**: Detection runs on smaller frames for better performance
- **Accurate Targeting**: Mouse points to actual center of bounding boxes
- **Debug Information**: Shows scaling factors and coordinate conversion

## Configuration Options

### Target Priority Selection
Choose from predefined targeting modes:

1. **Head & Face (Highest Priority)**
   - Targets: head, face
   - Best for: Precision targeting

2. **Head Only**
   - Targets: head only
   - Best for: Maximum precision

3. **Face Only**
   - Targets: face only
   - Best for: Facial targeting

4. **Head, Face & Torso**
   - Targets: head, face, torso
   - Best for: Upper body targeting

5. **Torso Only**
   - Targets: torso only
   - Best for: Body center targeting

6. **Full Body Priority**
   - Targets: head, face, torso, body
   - Best for: General body targeting

7. **Legs Priority**
   - Targets: left_leg, right_leg
   - Best for: Lower body targeting

8. **Arms Priority**
   - Targets: left_arm, right_arm
   - Best for: Arm targeting

9. **All Body Parts (Priority Order)**
   - Targets: All parts in priority order
   - Best for: Comprehensive targeting

### Mouse Control Settings
- **Mouse Smoothing**: 10-90% (default: 30%)
- **Target Confidence**: 30-90% (default: 50%)
- **Debug Targeting**: Enable/disable console output

## Usage

### Basic Usage
1. Start the application: `python3 simple_detector.py`
2. Go to Settings tab
3. Select desired Target Priority mode
4. Adjust Mouse Smoothing and Target Confidence
5. Enable Debug Targeting (optional)
6. Start detection
7. Enable mouse control
8. Watch the mouse target the highest priority body part

### Advanced Configuration
```python
# Example: Custom priority configuration
controller = MouseController()
controller.set_target_parts(['head', 'face', 'torso'])
controller.set_smoothing(0.5)  # 50% smoothing
controller.set_confidence_threshold(0.7)  # 70% confidence
controller.set_debug_mode(True)  # Enable debug output
```

### Advanced Usage

#### Custom Target Parts

You can select specific body parts for targeting:

1. In Settings, choose **Custom Selection**
2. Select the body parts you want to target
3. The system will prioritize them in the order selected

#### Debug Mode

Enable debug mode to see detailed targeting information:

```
🎯 Targeting head at (140, 100) confidence: 0.70
🎯 Processed coords: (140, 100) -> Screen coords: (140, 100)
📏 Scaling factors: X=1.50, Y=1.50
📏 Original: (1920, 1080), Processed: (1280, 720)
```

## Testing

### Test Scripts
- `test_targeting_system.py`: Comprehensive targeting system tests
- `test_stop_functionality.py`: Stop functionality tests
- `demo_stop_functionality.py`: Visual demonstration

### Manual Testing
1. Run the application
2. Enable debug mode
3. Start detection with human subjects
4. Enable mouse control
5. Observe targeting behavior
6. Adjust settings as needed

## Technical Implementation

### MouseController Class
```python
class MouseController:
    def __init__(self):
        # Priority ranking dictionary
        self.body_part_priority = {
            'head': 1, 'face': 2, 'torso': 3, 'body': 4,
            'left_leg': 5, 'right_leg': 5, 'left_arm': 6, 'right_arm': 6,
            'left_hand': 7, 'right_hand': 7, 'left_foot': 8, 'right_foot': 8,
            'person': 9
        }
    
    def _move_to_target(self):
        # Find best target based on priority and confidence
        # Move mouse to center of bounding box
        # Apply smoothing for natural movement
```

### Targeting Algorithm
1. **Filter detections** by confidence threshold
2. **Calculate priority** for each detection
3. **Select best target** (lowest priority number, highest confidence)
4. **Calculate center** of bounding box
5. **Apply smoothing** to mouse movement
6. **Move mouse** to target position

### Performance Considerations
- **60 FPS targeting**: Updates 60 times per second
- **Smooth movement**: Prevents jerky mouse behavior
- **Confidence filtering**: Reduces false positives
- **Priority caching**: Efficient priority lookups

## Troubleshooting

### Mouse Not Targeting Center

**Problem**: Mouse is not pointing to the center of bounding boxes.

**Solution**: The coordinate scaling fix ensures accurate targeting. If issues persist:

1. Enable debug mode to see scaling information
2. Check that scaling factors are correct
3. Verify frame sizes are being detected properly

### Jerky Mouse Movement

**Problem**: Mouse movement is jerky or erratic.

**Solution**:
1. The smoothing factor has been reduced to 0.15 for more linear movement
2. Movement duration is now dynamic based on distance
3. Check for performance issues or high FPS settings

### Body Parts Not Filtering

**Problem**: Unchecked body parts are still being detected/drawn.

**Solution**:
1. Ensure you're in "Custom Selection" mode
2. Check that the body parts you want to ignore are unchecked
3. Changes apply immediately when detection is running
4. Check console output for filtering information

### Low Accuracy

**Problem**: Targeting accuracy is poor.

**Solution**:
1. Increase confidence threshold
2. Use higher priority body parts
3. Ensure good lighting and clear detection
4. Check model quality and training data

### Performance Issues

**Problem**: System is slow or laggy.

**Solution**:
1. Use smaller detection models (yolov8n-pose.pt)
2. Reduce detection FPS
3. Use smaller frame sizes
4. Close other applications

## Future Enhancements

### Potential Improvements
1. **Dynamic Priority**: Adjust priority based on context
2. **Multi-target Support**: Target multiple body parts simultaneously
3. **Prediction**: Predict movement for moving targets
4. **Custom Priorities**: User-defined priority rankings
5. **Target History**: Remember previous targets
6. **Adaptive Smoothing**: Adjust smoothing based on target size

### Advanced Features
1. **Target Locking**: Lock onto specific targets
2. **Priority Profiles**: Save/load priority configurations
3. **Target Analytics**: Track targeting accuracy
4. **Custom Targeting**: Define custom targeting regions
5. **Integration**: Connect with other automation tools

## Technical Details

### Coordinate Scaling

The system handles frame resizing for performance while maintaining accurate targeting:

```python
# Calculate center in processed frame coordinates
center_x = x + w // 2
center_y = y + h // 2

# Scale to original screen coordinates
screen_x = int(center_x * scale_factor_x)
screen_y = int(center_y * scale_factor_y)
```

### Priority Logic

```python
# Priority: 1. Higher priority (lower number), 2. Higher confidence
if (priority < best_priority or 
    (priority == best_priority and confidence > best_confidence)):
    if confidence > confidence_threshold:
        best_target = detection
```

### Smoothing Algorithm

```python
# Apply smoothing for natural movement
smooth_x = int(last_x * (1 - smoothing_factor) + target_x * smoothing_factor)
smooth_y = int(last_y * (1 - smoothing_factor) + target_y * smoothing_factor)
```

## Testing

### Test Scripts

Run the test scripts to verify functionality:

```bash
# Test coordinate scaling
python3 test_coordinate_scaling.py

# Test targeting system
python3 test_targeting_system.py
```

### Manual Testing

1. **Coordinate Accuracy**: Enable debug mode and verify coordinates match screen position
2. **Priority Ranking**: Test different priority modes and verify correct targeting
3. **Confidence Filtering**: Test with low-confidence detections
4. **Smooth Movement**: Verify mouse movement is natural and not jerky

## Troubleshooting

### Mouse Not Targeting Center

**Problem**: Mouse is not pointing to the center of bounding boxes.

**Solution**: The coordinate scaling fix ensures accurate targeting. If issues persist:

1. Enable debug mode to see scaling information
2. Check that scaling factors are correct
3. Verify frame sizes are being detected properly

### Jerky Mouse Movement

**Problem**: Mouse movement is jerky or erratic.

**Solution**:
1. The smoothing factor has been reduced to 0.15 for more linear movement
2. Movement duration is now dynamic based on distance
3. Check for performance issues or high FPS settings

### Body Parts Not Filtering

**Problem**: Unchecked body parts are still being detected/drawn.

**Solution**:
1. Ensure you're in "Custom Selection" mode
2. Check that the body parts you want to ignore are unchecked
3. Changes apply immediately when detection is running
4. Check console output for filtering information

### Low Accuracy

**Problem**: Targeting accuracy is poor.

**Solution**:
1. Increase confidence threshold
2. Use higher priority body parts
3. Ensure good lighting and clear detection
4. Check model quality and training data

### Performance Issues

**Problem**: System is slow or laggy.

**Solution**:
1. Use smaller detection models (yolov8n-pose.pt)
2. Reduce detection FPS
3. Use smaller frame sizes
4. Close other applications

## Recent Improvements

### Mouse Targeting Based on Body Part Selection (Latest Feature)
- **User Control**: Mouse only targets the body parts you select
- **Confidence Based**: Among selected parts, targets highest confidence
- **Real-time Updates**: Changes apply immediately when checkboxes change
- **No Fixed Priority**: Removed hardcoded priority system
- **Flexible Targeting**: Choose exactly what to target

### Person vs Body Parts Detection (Previous Feature)
- **Person Checkbox**: Added "Person" to body parts selection
- **Flexible Detection**: Choose between full person or specific body parts
- **Precision Control**: Detect only head without person bounding boxes
- **Mixed Detection**: Combine person and specific body parts
- **Performance Optimization**: Detect only what you need

### Body Parts Filtering (Previous Fix)
- **Complete Filtering**: Unchecked body parts are completely ignored
- **No Visual Clutter**: Bounding boxes are only drawn for selected body parts
- **Real-time Updates**: Changes apply immediately when checkboxes are toggled
- **Mouse Control**: Mouse only targets selected body parts
- **Debug Output**: Console shows filtering information

### Mouse Movement Improvements (Previous Fix)
- **Linear Movement**: Reduced smoothing factor (0.15) for more natural movement
- **Dynamic Duration**: Movement duration adjusts based on distance
- **Accurate Targeting**: Improved coordinate scaling for center targeting
- **Smooth Transitions**: Better handling of target changes
- **Performance**: Optimized movement calculations

### Coordinate Scaling (Previous Fix)
- **Accurate Targeting**: Mouse points to exact center of bounding boxes
- **Frame Resizing**: Handles performance optimization without losing accuracy
- **Cross-platform**: Works on different screen resolutions
- **Debug Information**: Shows scaling factors and coordinate conversion

## Detection Options

### Person vs Body Parts Detection

You can now choose between detecting full "Person" or specific body parts like "Head":

#### Option A: Detect Only Head (No Person)
- Uncheck "Person" checkbox
- Check "Head" checkbox
- Uncheck all other body parts
- **Result**: Only head bounding boxes, no full person boxes
- **Use case**: Precise head tracking for targeting

#### Option B: Detect Person Only
- Check "Person" checkbox
- Uncheck all body parts (head, face, torso, etc.)
- **Result**: Only full person bounding boxes
- **Use case**: General person presence detection

#### Option C: Detect Person + Specific Body Parts
- Check "Person" checkbox
- Check "Head" and "Face" checkboxes
- **Result**: Both person boxes and head/face boxes
- **Use case**: Both general and precise detection

#### Option D: Detect Only Body Parts (No Person)
- Uncheck "Person" checkbox
- Check "Head", "Face", "Torso" checkboxes
- **Result**: Only body part boxes, no full person boxes
- **Use case**: Specific body part tracking without person clutter

### Detection Modes

1. **All Body Parts**: Detects everything (person + all body parts)
2. **Person Only**: Detects only full person
3. **Custom Selection**: Choose exactly what to detect

### Benefits

- **More precise control** over what gets detected
- **Avoid visual clutter** from unwanted detections
- **Optimize performance** by detecting only what you need
- **Better targeting accuracy** for specific use cases
- **Flexible detection strategies** for different scenarios

## Multi-Monitor Support

The targeting system correctly handles multi-monitor setups by:

1. **Monitor offset calculation**: Uses monitor information from the screen capture system
2. **Absolute coordinate conversion**: Converts relative coordinates to absolute screen coordinates
3. **Coordinate scaling**: Handles frame resizing for performance optimization

### Coordinate Calculation Process

1. **Detection coordinates**: YOLO provides coordinates in the processed frame (e.g., 640x480)
2. **Scale to original**: Convert to original monitor resolution using scaling factors
3. **Add monitor offset**: Add the monitor's position in the global screen coordinate system
4. **Apply smoothing**: Use exponential smoothing for natural movement
5. **Move mouse**: Use pyautogui to move to the calculated absolute coordinates

Example for a secondary monitor:
```
Processed frame: (320, 240)  # Center of 640x480
Scaled to monitor: (900, 584)  # Scaled to monitor resolution
Monitor offset: (3008, 991)   # Monitor position in global coordinates
Absolute screen: (3908, 1575) # Final mouse position
```

## Debug Output

When debug mode is enabled, the system provides detailed information:

```
🎯 Targeting head at (1504, 846) confidence: 0.85
🎯 Processed coords: (320, 240) -> Screen coords: (1504, 846)
🎯 Monitor offset: (0, 0)
🎯 Absolute coords: (1504, 846)
🎯 Movement: duration=0.045s, distance=125.3px
📏 Scaling factors: X=4.70, Y=3.52
📏 Original: (3008, 1692), Processed: (640, 480)
```

## Performance Considerations

- **Frame resizing**: Large frames are resized to 1280px width for performance
- **Coordinate caching**: Scaling factors are cached to avoid recalculation
- **Smooth movement**: Movement duration is calculated based on distance
- **Thread safety**: Mouse control runs in a separate thread to prevent GUI freezing

## Future Enhancements

- **Prediction**: Predict target movement for better tracking
- **Multiple targets**: Support for targeting multiple detections simultaneously
- **Custom priorities**: User-defined priority ranking
- **Movement patterns**: Different movement styles (linear, curved, etc.)
- **Target history**: Remember and avoid previously targeted positions 