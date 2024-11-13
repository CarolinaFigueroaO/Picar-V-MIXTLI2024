'''
Andrea Carolina Figueroa Orihuela
Enginnering in Computer Technologies - ITESM

May 2024
'''

#Import libraries
import cv2
import numpy as np
from picar import back_wheels, front_wheels
import picar
import time

#Define global variables
#----------------------
alphaPos = 60
betaPos = 48

velocity = 70
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


#Define an empty function
def empty(a):
    pass

#Create trackbars for the brightness adjustment
def createTrackbars():
    cv2.namedWindow("Parameters") # Create a window for the trackbars
    cv2.resizeWindow("Parameters",640,240) 
    cv2.createTrackbar("Alpha", "Parameters", 0, 300, empty)
    cv2.createTrackbar("Beta", "Parameters", 0, 100, empty)
    cv2.setTrackbarPos("Alpha", "Parameters", alphaPos)
    cv2.setTrackbarPos("Beta", "Parameters", betaPos)

#Adjust the brightness of the image
def brightnessAjustment(img):
    alpha = cv2.getTrackbarPos("Alpha", "Parameters") / 100
    beta = cv2.getTrackbarPos("Beta", "Parameters")
    imgBrightness = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return imgBrightness    

#Detect the blue color (obstacles) in the image
def blueDetection(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([90, 50, 70])
    upper = np.array([140, 255, 255])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def finishDetection(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #orange detection
    lower = np.array([0, 100, 100])
    upper = np.array([20, 255, 255])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask


#Avoid the blue obstacles
def avoidBlue(mask):
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        # Calculate the moment of the contour
        M = cv2.moments(largest_contour)
        if area >= min_area:
            if M["m00"] != 0:
                bw.speed = medium_velocity
                incrementObstacles()
                # Calculate the coordinate of the center of the contour in X
                cX = int(M["m10"] / M["m00"])
                width = mask.shape[1]

                # Decide the direction of the movement based on the X position
                if cX < width // 20:
                    direction = "Forward"
                    fw.turn(forward)
                elif cX > 9.5 * width // 10:
                    direction = "Forward"
                    fw.turn(forward)
                elif cX < width // 2:
                    direction = "Turn right"
                    fw.turn(right)
                elif cX > width // 2:
                    direction = "Turn left"
                    fw.turn(left)
                else:
                    direction = "Forward"
                    fw.turn(forward)
                
                print(f"Center of the obstacle in X: {cX}, {direction}")
        else:
            print("No obstacles detected")

#Increment the number of obstacles
def incrementObstacles():
    global last
    global now
    now = time.time()
    if (now - last) >= 3:
        global obstacles
        obstacles += 1
        last = time.time()

#Avoid the blue obstacles with a big movement
def bigMovement():
    now = time.time()
    while time.time() - now < 1.5:
        fw.turn(right)
    now = time.time()
    while time.time() - now < 1:
        fw.turn(left)
    
#Get the lines of the path from the image
def getLines(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 200])
    upper = np.array([180, 50, 255])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

#Get the area of the path from the image
def getArea(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 0])
    upper = np.array([179, 255, 100])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

#Avoid the lines of the path
def avoidLines(mask):
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
                # Calcula la coordenada del centro del contorno en X
                cX = int(M["m10"] / M["m00"])
                width = mask.shape[1]

                # Decide la dirección del movimiento basado en la posición X
                if cX < width // 2 and cX > width // 4:
                    direction = "Turn right"
                    fw.turn(right)
                elif cX > width // 2 and cX < 3 * width // 4:
                    direction = "Turn left"
                    fw.turn(left)

                else:
                    direction = "Forward"
                    fw.turn(forward)
                
                print(f"Center of the path in X: {cX}, {direction}")
            else:
                print("No lines detected")
    else:
        print("No lines detected")

def main():
    cap = cv2.VideoCapture(0)
    createTrackbars()
    bw.speed = velocity

    # Loop principal for the routine
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = brightnessAjustment(frame)
        blue = blueDetection(frame)
        lines = getLines(frame)
        orange = finishDetection(frame)
        
        if orange is not None:
            bw.stop()
            break
        if lines is not None:
            avoidLines(lines)
        if blue is not None:
            avoidBlue(blue)
        else:
            bw.speed = velocity

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
    bw.speed = stop
    bw.stop()
    print("OBSTACLES FOUND: ", obstacles)

if __name__ == "__main__":
    last = time.time()
    picar.setup()
    bw = back_wheels.Back_Wheels()
    fw = front_wheels.Front_Wheels()
    fw.turn(forward)
    main()
