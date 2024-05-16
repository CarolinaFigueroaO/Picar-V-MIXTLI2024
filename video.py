import cv2
import numpy as np
import time
import picar


cap = cv2.VideoCapture(0)

def main():
    while True:
        _, frame = cap.read()
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break