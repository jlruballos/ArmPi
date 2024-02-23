#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import math
import Camera
import numpy as np
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

class ColorTracker:
    def __init__(self):
        self.__target_color = ('red',)
        self.__isRunning = False
        self.__size = (640, 480)
        self.__roi = ()
        self.__get_roi = False
        self.__start_pick_up = False
        self.__last_x = 0
        self.__last_y = 0
        self.__world_x = 0
        self.__world_y = 0

    def set_target_color(self, target_color):
        self.__target_color = target_color
    
    def get_target_color(self):
        # Assuming __target_color is a tuple and you want the first element
        return self.__target_color[0]

    def start(self):
        self.__isRunning = True

    def stop(self):
        self.__isRunning = False

    def run(self, img):
        detected = False  # Default detection status
        x, y = 0, 0  # Default coordinates

        if not self.__isRunning:
            return img, detected, x, y


        frame_resize = cv2.resize(img, self.__size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        
        if self.__get_roi and self.__start_pick_up:
            self.__get_roi = False
            frame_gb = getMaskROI(frame_gb, self.__roi, self.__size)

        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)
        detect_color = self.__target_color[0]

        frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        areaMaxContour, area_max = self.getAreaMaxContour(contours)
        if area_max > 2500:  # Found the largest area
            detected = True  # Update detection status
            rect = cv2.minAreaRect(areaMaxContour)
            box = np.int0(cv2.boxPoints(rect))
            
            self.set_rgb(detect_color)

            self.__roi = getROI(box)  # Update ROI
            self.__get_roi = True

            square_length = 20  # Define square_length based on your application needs
            img_centerx, img_centery = getCenter(rect, self.__roi, self.__size, square_length)  # Use the fixed square_length

            # Convert to real-world coordinates, ensure these functions are defined or implement them as needed
            self.__world_x, self.__world_y = convertCoordinate(img_centerx, img_centery, self.__size)
            
            cv2.drawContours(img, [box], -1, range_rgb[detect_color], 2)
            cv2.putText(img, f'({self.__world_x},{self.__world_y})', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[detect_color], 1)  # Draw the center point

            # Compare with the previous coordinates to determine if there is movement
            distance = math.sqrt(pow(self.__world_x - self.__last_x, 2) + pow(self.__world_y - self.__last_y, 2))
            self.__last_x, self.__last_y = self.__world_x, self.__world_y
            x, y = self.__world_x, self.__world_y  # Update coordinates

        return img, detected, x, y

    def getAreaMaxContour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:
            contour_area_temp = math.fabs(cv2.contourArea(c))
            if contour_area_temp > contour_area_max:
                if contour_area_temp > 300:
                    contour_area_max = contour_area_temp
                    area_max_contour = c

        return area_max_contour, contour_area_max
    
    #Set the color of the RGB light on the expansion board to match the color to be tracked.
    def set_rgb(self, color):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()

""" if __name__ == '__main__':
    tracker = ColorTracker()
    tracker.set_target_color(('green',))
    tracker.start()

    my_camera = Camera.Camera()
    my_camera.camera_open()

    while True:
        img = my_camera.frame
        if img is not None:
            frame = tracker.run(img)
            cv2.imshow('Frame', frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC key
                break

    my_camera.camera_close()
    cv2.destroyAllWindows() """
