import cv2
import numpy as np
import time
from picar import back_wheels, front_wheels
import picar

cap = cv2.VideoCapture(0)


width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

meanX = int(width/2)

threshold1 = 240
threshold2 = 255
alphaPos = 100
betaPos = 68

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

def getLines(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 200])
    upper = np.array([180, 50, 255])
    mask = cv2.inRange(imgHSV, lower, upper)
    getCenterX(mask)
    return mask

def getArea(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 0])
    upper = np.array([179, 255, 100])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask


def getContours(lines, frame):
    contours, _ = cv2.findContours(lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Draw the contours on the image
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)
    return contours


def getCenterX(mask):
    # Encuentra los contornos en la máscara
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        # Si no hay contornos, retorna None o algún valor por defecto
        return None
    
    # Lista para almacenar los centros X de los contornos
    centerX_list = []
    
    for contour in contours:
        # Calcula los momentos del contorno
        M = cv2.moments(contour)
        
        if M["m00"] != 0:
            # Calcula el centroide del contorno
            cX = int(M["m10"] / M["m00"])
            centerX_list.append(cX)
    
    if len(centerX_list) == 0:
        # Si no hay centros calculados, retorna None o algún valor por defecto
        return None
    
    # Calcula el promedio de los centros X
    centerX = int(np.mean(centerX_list))
    print(centerX)
    #return centerX


    if centerX < (meanX - 150):
        print("Turn left")
        fw.turn(180)
    elif centerX > (meanX + 150):
        print("Turn right")
        fw.turn(0)
    else:
        print("Centered")
        fw.turn(90)

def angleAdjustment(lines, frame):
    contours = getContours(lines,frame)
    # Initialize a list to store the angles of the contours
    if len(contours) > 0:
        x, y, w, h = cv2.boundingRect(contours[0]) # Get the rectangle that encloses the contour
        box = cv2.minAreaRect(contours[0]) 
        (x_min, y_min), (w_min, h_min), angle = box # Get the width, height and angle of the rectangle
        if angle < -45: 
            angle = 90 + angle
        if w_min < h_min and angle > 0:
            angle = (90 - angle) * -1
        if w_min > h_min and angle < 0:
            angle = 90 + angle
        if angle < 0:
            turn = 90 + angle
            turn = int(turn)
            if turn < 10:    # If the turn is less than 10 we consider it centered
                print("Centered")
            else:
                print("Turn right",  turn) # If the turn is greater than 10 we consider it a turn to the right
                fw.turn(0)
                return
        if angle > 0:
            turn = 90 - angle
            turn = int(turn)
            if turn < 10:   # If the turn is less than 10 we consider it centered
                print("Centered")
                fw.turn(90)
            else: # If the turn is greater than 10 we consider it a turn to the left
                print("Turn left", turn) 
                fw.turn(180)
                return


def main():

    bw.speed = 20
    createTrackbars()
    while True:
        _, frame = cap.read()
        frame =  brightnessAjustment(frame)
        lines = getLines(frame)
        angleAdjustment(lines, frame)
        area = getArea(frame)
        detections = cv2.hconcat([lines, area])
        cv2.imshow("Detections", detections)
        cv2.imshow("Frame", frame)
        k = cv2.waitKey(30) 
        if k == 27: #Define the key to close the window
            break  
    cap.release()
    cv2.destroyAllWindows()
    bw.speed = 0
    bw.stop()
        

if __name__ == "__main__":
    picar.setup()
    bw = back_wheels.Back_Wheels()
    fw = front_wheels.Front_Wheels()
    main()

