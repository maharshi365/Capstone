#!/usr/bin/env python3.5

'''
TODO

implement directions

take contour and get output

only do one calculation per direction


do yellow detection


station IDS

'''



import threading
import queue
import cv2
import numpy as np
#import Motors

RED_LOW = 150
RED_HIGH = 200

GREEN_LOW = 60
GREEN_HIGH = 100

YELLOW_LOW = 0
YELLOW_HIGH = 40

class Navigator(threading.Thread):
    def __init__(self, opt):
        threading.Thread.__init__(self)

        #motor controller class
        #self.motors = Motors.Motors()

        #image related fields
        self.cap = cv2.VideoCapture(0)
        _, self.frame = self.cap.read()
        self.lastFrame = None
        self.hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        
        self.h, self.w = self.frame.shape[:2]
        self.opt = opt

        self.red = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.green = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.yellow = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.draw = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        #center of line contour
        self.center = (0, 0)

    def __del__(self):
        self.cap.release()

    def update(self):
        #update logic run each tick

        self.lastFrame = self.frame
        _ , self.frame = self.cap.read()
        self.hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        self.draw = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        self.processLine()
        self.detect()

    def setOpt(self, newopt):
        self.opt = newopt

    def processLine(self):
        
        try:
            
            #threshold by hsv value
            r = cv2.inRange(self.hsv, (RED_LOW, 10, 15), (RED_HIGH ,255, 200))
            g = cv2.inRange(self.hsv, (GREEN_LOW, 10, 15), (GREEN_HIGH, 255, 200))
            y = cv2.inRange(self.hsv, (YELLOW_LOW,10, 15), (YELLOW_HIGH, 255, 200))

            #perform open morphological operation to fill region
            r = cv2.morphologyEx(r, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3,3)))
            g = cv2.morphologyEx(g, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3,3)))
            y = cv2.morphologyEx(y, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3,3)))
        
            #median blur to fill region
            self.red = cv2.medianBlur(r, 3)
            self.green = cv2.medianBlur(g, 3)
            self.yellow = cv2.medianBlur(y, 3)

            #get contours
            yc, _ = cv2.findContours(self.yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            rc, _ = cv2.findContours(self.red, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            gc, _ = cv2.findContours(self.green, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            cv2.drawContours(self.draw, [max(yc, key=cv2.contourArea)], 0, (0,255,255), -1) 
            cv2.drawContours(self.draw, [max(gc, key=cv2.contourArea)], 0, (0,255,0), -1) 
            cv2.drawContours(self.draw, [max(rc, key=cv2.contourArea)], 0, (0,0,255), -1) 

        except TypeError as e:
            print(e)

        
    def detect(self):
        pass

    def run(self):
        while(True):
            self.update()
 