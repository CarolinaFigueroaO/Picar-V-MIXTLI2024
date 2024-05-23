import cv2
import numpy as np
from picar import back_wheels, front_wheels
import picar
import time


threshold1 = 240
threshold2 = 255
alphaPos = 60
betaPos = 48

min_area = 3000
max_area = 80000

velocity = 70

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
                bw.speed = 50
                # Calcula la coordenada del centro del contorno en X
                cX = int(M["m10"] / M["m00"])
                width = mask.shape[1]

                # Decide la dirección del movimiento basado en la posición X
                if cX < width // 20:
                    direction = "Adelante"
                    fw.turn(90)
                elif cX > 9.5 * width // 10:
                    direction = "Adelante"
                    fw.turn(90)
                elif cX < width // 3:
                    direction = "Girar a la derecha"
                    fw.turn(180)
                elif cX > 2 * width // 3:
                    direction = "Girar a la izquierda"
                    fw.turn(0)
                else:
                    direction = "Movimiento brusco"
                    bigMovement()
                
                print(f"Centro del contorno azul en X: {cX}, {direction}")
        else:
            print("No se pudo calcular el centro del contorno")


def bigMovement():
    now = time.time()
    while time.time() - now < 1:
        fw.turn(180)
    now = time.time()
    while time.time() - now < 1:
        fw.turn(0)
    


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

def closeCurve(contours):
    print("Close curve")
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
                
                return
        if angle > 0:
            turn = 90 - angle
            turn = int(turn)
            if turn < 10:   # If the turn is less than 10 we consider it centered
                print("Centered")
            else: # If the turn is greater than 10 we consider it a turn to the left
                print("Turn left", turn) 
                return

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
                # Calcula la coordenada del centro del contorno en X
                cX = int(M["m10"] / M["m00"])
                width = mask.shape[1]

                # Decide la dirección del movimiento basado en la posición X
                if cX < width // 2 and cX > width // 4:
                    direction = "Girar a la derecha"
                    fw.turn(180)
                elif cX > width // 2 and cX < 3 * width // 4:
                    direction = "Girar a la izquierda"
                    fw.turn(0)

                else:
                    direction = "Adelante"
                    fw.turn(90)
                
                print(f"Centro de linea en X: {cX}, {direction}")
            else:
                print("No se pudo calcular el centro del contorno")
    else:
        print("No se detectaron lineas")

def main():
    # Suponiendo que estás capturando video desde una cámara
    cap = cv2.VideoCapture(0)
    bw.speed = velocity
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
        else:
            bw.speed = velocity
        # Muestra el frame y la máscara para depuración
        cv2.imshow("Frame", frame)
        cv2.imshow("Blue", blue)
        cv2.imshow("Lines", lines)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    bw.speed = 0
    bw.stop()

if __name__ == "__main__":
    picar.setup()
    bw = back_wheels.Back_Wheels()
    fw = front_wheels.Front_Wheels()
    fw.turn(90)
    main()
