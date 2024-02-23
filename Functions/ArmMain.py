#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import threading
from OnlyColorTracking import ColorTracker
from MotionController import MotionController
import Camera

class MainProgram:
    def __init__(self):
        self.tracker = ColorTracker()
        self.motionController = MotionController()
        self.camera = Camera.Camera()
        self.pick_and_place_thread = None

    def pick_and_place(self, x, y, color):
        self.motionController.pickAndPlace(x, y, color)
        # After pick-and-place, optionally move to an idle position
        self.motionController.moveToIdlePosition()
    
    def run(self):
        self.tracker.start()
        self.motionController.start()
        self.camera.camera_open()

        try:
            while True:
                img = self.camera.frame
                if img is not None:
                    frame, detected, x, y = self.tracker.run(img)  # Assume run() returns also detection status and coordinates
                    
                    if detected:
                        # Ensure previous pick-and-place operation is complete before starting a new one
                        if self.pick_and_place_thread is None or not self.pick_and_place_thread.is_alive():
                            color = self.tracker.get_target_color()
                            # Start pick-and-place operation in a separate thread
                            self.pick_and_place_thread = threading.Thread(target=self.pick_and_place, args=(x, y, color))
                            self.pick_and_place_thread.start()
                        
                    cv2.imshow('Frame', frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC key
                        break

        finally:
            self.camera.camera_close()
            cv2.destroyAllWindows()
            self.tracker.stop()
            self.motionController.stop()
            if self.pick_and_place_thread is not None:
                self.pick_and_place_thread.join()  # Ensure the pick-and-place thread has completed

if __name__ == '__main__':
    program = MainProgram()
    program.run()
