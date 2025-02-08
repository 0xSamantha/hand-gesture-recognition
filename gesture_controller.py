iimport pyautogui
import time
import cv2 as cv
import numpy as np
from model import KeyPointClassifier

class GestureGameController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        self._initialize_classifier()
        
        self.gesture_mappings = {
            'Open': self.handle_open,
            'Close': self.handle_close,
            'Pointer': self.handle_aim,
            'OK': self.handle_reload,
            'Thumbs Up': self.handle_jump,
            'Peace Sign': self.weapon_switch,
            'Three Fingers': self.handle_heal,
            'Palm Up': self.move_forward,
            'Palm Down': self.move_backward
        }
        
        self.is_shooting = False
        self.is_moving = False
        self.previous_gesture = None
        
    def _initialize_classifier(self):
        self.keypoint_classifier = KeyPointClassifier()
        
    def process_landmarks(self, landmarks, gesture_id):
        """Process landmarks and execute corresponding gesture action"""
        if gesture_id in self.gesture_mappings:
            self.gesture_mappings[gesture_id](landmarks)
            self.previous_gesture = gesture_id
    
    def handle_open(self, _):
        if self.is_shooting:
            pyautogui.mouseUp(button='left')
            self.is_shooting = False
    
    def handle_close(self, _):
        if not self.is_shooting:
            pyautogui.mouseDown(button='left')
            self.is_shooting = True
    
    def handle_aim(self, landmarks):
        if landmarks and len(landmarks) > 8:
            screen_width, screen_height = pyautogui.size()
            x, y = landmarks[8]  # Index finger tip
            
            # Normalize coordinates
            scaled_x = min(max(int((x / 640) * screen_width), 0), screen_width)
            scaled_y = min(max(int((y / 480) * screen_height), 0), screen_height)
            
            # Smooth mouse movement
            pyautogui.moveTo(scaled_x, scaled_y, duration=0.1)
    
    def handle_reload(self, _):
        pyautogui.press('r')
        time.sleep(0.5)  # Prevent rapid reloading
    
    def handle_jump(self, _):
        pyautogui.press('space')
        time.sleep(0.3)  # Prevent jump spam
    
    def weapon_switch(self, _):
        pyautogui.press('1')
        time.sleep(0.3)  # Prevent rapid switching
    
    def handle_heal(self, _):
        pyautogui.press('4')
        time.sleep(1)  # Give time for healing animation
    
    def move_forward(self, _):
        if not self.is_moving:
            pyautogui.keyDown('w')
            self.is_moving = True
        else:
            pyautogui.keyUp('w')
            self.is_moving = False
    
    def move_backward(self, _):
        if not self.is_moving:
            pyautogui.keyDown('s')
            self.is_moving = True
        else:
            pyautogui.keyUp('s')
            self.is_moving = False
    
    def cleanup(self):
        """Release all keys and buttons on exit"""
        keys_to_release = ['w', 's', 'a', 'd', 'ctrl']
        for key in keys_to_release:
            pyautogui.keyUp(key)
        pyautogui.mouseUp(button='left')
        self.is_shooting = False
        self.is_moving = False

def pre_process_landmarks(landmark_list):
    """Convert landmarks to model input format"""
    temp_landmark_list = []
    base_x, base_y = 0, 0

    for index, landmark in enumerate(landmark_list):
        if index == 0:
            base_x, base_y = landmark[0], landmark[1]

        temp_landmark_list.append([landmark[0] - base_x, landmark[1] - base_y])

    # Convert to relative coordinates
    temp_landmark_list = list(np.array(temp_landmark_list).flatten())

    # Normalize
    max_value = max(map(abs, temp_landmark_list))
    def normalize_(n): return n / max_value if max_value != 0 else 0

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list