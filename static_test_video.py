'''
Andrea Carolina Figueroa Orihuela
Enginnering in Computer Technologies - ITESM

May 2024
'''

import cv2
import numpy as np

import time

#----------------------
alphaPos = 60
betaPos = 48

velocity = 90
#-----------------------

medium_velocity = 50

global obstacles
obstacles = 0

threshold1 = 240
threshold2 = 255

min_area = 3000
max_area = 80000

right = 180
left = 0
forward = 90
stop = 0

subwidth = 320
subheight = 240

def empty(a): # Funcion para los trackbars
    pass


def createTrackbars():
    cv2.namedWindow("Parameters") # Create a window for the trackbars
    cv2.resizeWindow("Parameters",640,240) 
    cv2.createTrackbar("Alpha", "Parameters", 0, 300, empty)
    cv2.createTrackbar("Beta", "Parameters", 0, 100, empty)
    cv2.setTrackbarPos("Alpha", "Parameters", alphaPos)
    cv2.setTrackbarPos("Beta", "Parameters", betaPos)


def brightnessAjustment(img):
    alpha = cv2.getTrackbarPos("Alpha", "Parameters") / 100
    beta = cv2.getTrackbarPos("Beta", "Parameters")
    imgBrightness = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return imgBrightness    


def blueDetection(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([90, 50, 70])
    upper = np.array([140, 255, 255])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def evitBlue(mask):
    # Encuentra contornos en la máscara
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Encuentra el contorno más grande por área
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        # Calcula el momento del contorno
        M = cv2.moments(largest_contour)
        if area >= min_area:
            if M["m00"] != 0:
                incrementObstacles()
                # Calcula la coordenada del centro del contorno en X
                cX = int(M["m10"] / M["m00"])
                width = mask.shape[1]

                # Decide la dirección del movimiento basado en la posición X
                if cX < width // 20:
                    direction = "Turn right"
                elif cX > 9.5 * width // 10:
                    direction = "Forward"
                elif cX < width // 2:
                    direction = "Turn right"
                elif cX > width // 2:
                    direction = "Turn left"
                else:
                    direction = "Forward"
                
                print(f"Center of the obstacle in X: {cX}, {direction}")
        else:
            print("No obstacle detected")

def incrementObstacles():
    global last
    global now
    now = time.time()
    if (now - last) >= 3:
        global obstacles
        obstacles += 1
        last = time.time()


def getLines(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 200])
    upper = np.array([180, 50, 255])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def getArea(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 0])
    upper = np.array([179, 255, 100])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def pause():
    now = time.time()
    while time.time() - now < 2:
        pass
    return

def adjustSpeedBasedOnInclination(angle):
    print(f"INCLINATION: {angle}")
    if (angle < 0 and angle > 45) or (angle > 135 and angle < 180):
        print(f"LOW SPEED ----------------")
    else:
        print(f"NORMAL SPEED")


def evitLines(mask):
        # Encuentra contornos en la máscara
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Encuentra el contorno más grande por área
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        print("AREA:" , area)
        # Calcula el momento del contorno
        M = cv2.moments(largest_contour)
        if area >= min_area:
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                width = mask.shape[1]
                if len(largest_contour) >= 5: 
                    ellipse = cv2.fitEllipse(largest_contour)
                    angle = ellipse[2]  
                    if angle > 90:
                        inclination_direction = "right"
                        normalized_angle = angle - 90
                    else:
                        inclination_direction = "left"
                        normalized_angle = angle + 90
                    
                    adjustSpeedBasedOnInclination(normalized_angle)


                # Decide la dirección del movimiento basado en la posición X
                if cX < width // 2 and cX > width // 4:
                    direction = "Turn right"
                elif cX > width // 2 and cX < 3 * width // 4:
                    direction = "Turn left"

                else:
                    direction = "Forward"
                print(f"Center of the path in X: {cX}, {direction}")
            else:
                print("Can't detect the center of the path")
    else:
        print("No lines detected")

def main():
    # Suponiendo que estás capturando video desde una cámara
    cap = cv2.VideoCapture(0)
    createTrackbars()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = brightnessAjustment(frame)
        blue = blueDetection(frame)
        lines = getLines(frame)
        if lines is not None:
            evitLines(lines)
        if blue is not None:
            evitBlue(blue)

        frame = cv2.resize(frame, (subwidth, subheight))
        blue = cv2.resize(blue, (subwidth, subheight))
        lines = cv2.resize(lines, (subwidth, subheight))

        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        if len(blue.shape) == 2:
            blue = cv2.cvtColor(blue, cv2.COLOR_GRAY2BGR)
        if len(lines.shape) == 2:
            lines = cv2.cvtColor(lines, cv2.COLOR_GRAY2BGR)
        # Muestra el frame y la máscara para depuración
        videos = np.hstack((frame, blue, lines))
        cv2.imshow("Parameters", videos)

        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    last = time.time()
    main()
