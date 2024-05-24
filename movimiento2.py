import cv2
import numpy as np
from picar import back_wheels, front_wheels
import picar
import time

#----------------------
alphaPos = 60
betaPos = 48

velocity = 90
#-----------------------

medium_velocity = 50

global state, obstacles
obstacles = 0

threshold1 = 240
threshold2 = 255

min_area = 3000
max_area = 80000

right = 180
left = 0
forward = 90
stop = 0


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
                bw.speed = medium_velocity
                incrementObstacles()
                # Calcula la coordenada del centro del contorno en X
                cX = int(M["m10"] / M["m00"])
                width = mask.shape[1]

                # Decide la dirección del movimiento basado en la posición X
                if cX < width // 20:
                    direction = "Adelante"
                    fw.turn(forward)
                elif cX > 9.5 * width // 10:
                    direction = "Adelante"
                    fw.turn(forward)
                elif cX < width // 2:
                    direction = "Girar a la derecha"
                    fw.turn(right)
                elif cX > width // 2:
                    direction = "Girar a la izquierda"
                    fw.turn(left)
                else:
                    direction = "Adelante"
                    fw.turn(forward)
                
                print(f"Centro del contorno azul en X: {cX}, {direction}")
        else:
            print("No se pudo calcular el centro del contorno")

def incrementObstacles():
    global last
    global now
    now = time.time()
    if (now - last) >= 3:
        global obstacles
        obstacles += 1
        last = time.time()


def bigMovement():
    now = time.time()
    while time.time() - now < 1.5:
        fw.turn(right)
    now = time.time()
    while time.time() - now < 1:
        fw.turn(left)
    


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
    createTrackbars()
    pause()
    bw.speed = velocity
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

if __name__ == "__main__":
    last = time.time()
    picar.setup()
    bw = back_wheels.Back_Wheels()
    fw = front_wheels.Front_Wheels()
    fw.turn(forward)
    main()
