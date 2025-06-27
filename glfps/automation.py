import pyautogui

class Automation:
    """
    Executes customizable mouse and keyboard actions based on detection results.
    """
    def __init__(self):
        pass

    def perform_action(self, detection_result):
        """
        If a detection is present, move the mouse to the center of the first bounding box.
        """
        if detection_result:
            bbox = detection_result[0]["bbox"]
            x, y, w, h = bbox
            center_x = x + w // 2
            center_y = y + h // 2
            pyautogui.moveTo(center_x, center_y) 