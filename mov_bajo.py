import cv2
import numpy as np
from picar import back_wheels, front_wheels
import picar
import time


threshold1 = 240
threshold2 = 255
alphaPos = 80
betaPos = 48

min_area = 10



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
        
        # Calcula el momento del contorno
        M = cv2.moments(largest_contour)
        
        if M["m00"] != 0:
            # Calcula la coordenada del centro del contorno en X
            cX = int(M["m10"] / M["m00"])
            width = mask.shape[1]

            # Decide la dirección del movimiento basado en la posición X
            if cX < width // 20:
                direction = "Adelante"
            elif cX > 9.5 * width // 10:
                direction = "Adelante"
            elif cX < width // 3:
                direction = "Girar a la derecha"
                fw.turn(0)
            elif cX > 2 * width // 3:
                direction = "Girar a la izquierda"
                fw.turn(180)
            else:
                direction = "Movimiento brusco"
                bigMovement()
            
            print(f"Centro del contorno azul en X: {cX}, {direction}")
        else:
            print("No se pudo calcular el centro del contorno")


def bigMovement():
    now = time.time()
    while time.time() - now < 1:
        bw.speed = 80
        fw.turn(0)
    now = time.time()
    while time.time() - now < 1:
        bw.speed = 60
        fw.turn(180)
    


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

def evitLines(mask):
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
                # Calcula la coordenada del centro del contorno en X
                cX = int(M["m10"] / M["m00"])
                width = mask.shape[1]

                # Decide la dirección del movimiento basado en la posición X
                if cX > width // 8:
                    direction = "Girar a la derecha"
                    fw.turn(0)
                elif cX > 7 * width // 8:
                    direction = "Girar a la izquierda"
                    fw.turn(180)

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
    bw.speed = 30
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
        #if blue is not None:
        #    evitBlue(blue)
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
    main()
