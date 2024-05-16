import cv2
import numpy as np


cap = cv2.VideoCapture("/dev/bus/usb/001/006")

def main():
    while True:
        _, frame = cap.read()
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break