#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import time
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board

AK = ArmIK()

class MotionController:
    def __init__(self):
        self.__isRunning = False
        self.servo1 = 500  # Initial servo position for the gripper
        self.servo2 = 500  # Initial servo position for rotation

        # Predefined coordinates for each color
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }

    def start(self):
        self.__isRunning = True
        self.initMove()

    def stop(self):
        self.__isRunning = False
        self.resetMove()

    def initMove(self):
        # Set initial positions
        Board.setBusServoPulse(1, self.servo1, 500)
        Board.setBusServoPulse(2, self.servo2, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def resetMove(self):
        # Reset to initial positions
        Board.setBusServoPulse(1, self.servo1, 500)
        Board.setBusServoPulse(2, self.servo2, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def openGripper(self):
        # Open the gripper to release the cube
        Board.setBusServoPulse(1, self.servo1 - 200, 500)  # Adjust the value based on your gripper's open position

    def closeGripper(self):
        # Close the gripper to grab the cube
        Board.setBusServoPulse(1, self.servo1, 500)  # Adjust the value based on your gripper's close position

    def moveTo(self, x, y, z):
        if not self.__isRunning:
            return

        # Move to the specified coordinates
        AK.setPitchRangeMoving((x, y, z), -90, -90, 0, 1500)
        time.sleep(1.5)  # Wait for the movement to complete

    def moveToColor(self, color):
        if color in self.coordinate:
            x, y, z = self.coordinate[color]
            self.moveTo(x, y, z)
        else:
            print(f"Color {color} not recognized or no predefined coordinate.")

    def pickAndPlace(self, color):
        # Open the gripper, move to the cube, close the gripper, lift, move to the target, open the gripper
        self.openGripper()
        time.sleep(1)  # Adjust timing based on your setup

        # Assuming you have the coordinates of the cube to pick
        # For example: self.moveTo(cube_x, cube_y, cube_z)
        # Lift the cube a bit: self.moveTo(cube_x, cube_y, cube_z + some_lift_height)

        self.closeGripper()
        time.sleep(1)  # Adjust timing based on your setup

        # Move to the target position based on the color
        self.moveToColor(color)

        self.openGripper()
        time.sleep(1)  # Adjust timing based on your setup

        # Optionally, move back to an initial/idle position
        self.initMove()
    
    def moveToIdlePosition(self):
        if not self.__isRunning:
            return
        
        # Example coordinates for an idle position
        idle_x, idle_y, idle_z = 0, 0, 15  # Adjust these coordinates based on your setup
        
        # Move to the idle position
        AK.setPitchRangeMoving((idle_x, idle_y, idle_z), -90, -90, 0, 1500)
        time.sleep(1.5)  # Wait for the movement to complete

