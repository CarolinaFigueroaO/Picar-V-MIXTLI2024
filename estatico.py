import cv2
import numpy as np
import time

alphaPos = 80
betaPos = 48

min_area = 100


subwindow_width = 320
subwindow_height = 240

velocity = 40
global state, obstacles
state = "Detenido"
obstacles = 0


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
    global movement
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
                if cX < width // 20:
                    movement = "Adelante"
                elif cX > 9.5 * width // 10:
                    movement = "Adelante"
                elif cX < width // 3:
                    movement = "Girar a la derecha"
                elif cX > 2 * width // 3:
                    movement = "Girar a la izquierda"
                else:
                    movement = "Movimiento brusco"
                    incrementObstacles()
                
                print(f"Centro del contorno azul en X: {cX}, {movement}")
            else:
                print("No se pudo calcular el centro del contorno")


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

def incrementObstacles():
    global obstacles
    obstacles += 1


def evitLines(mask):
    global movement
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
                if cX < width // 3 and cX > width // 6:
                    movement = "Girar a la derecha"
                elif cX > 2 * width // 3 and cX < 5 * width // 6:
                    movement = "Girar a la izquierda"

                else:
                    movement = "Adelante"
                
                print(f"Centro de linea en X: {cX}, {movement}")
            else:
                print("No se pudo calcular el centro de las lineas")
    else:
        print("No se detectaron lineas")


def displayInterface(frame, blue, lines):
    cv2.putText(frame, "ORIGINAL FRAME", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(blue, "BLUE FIGURES", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(lines, "DELIMITER LINES", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    velocity_img = np.zeros((subwindow_height, subwindow_width, 3), dtype=np.uint8)
    cv2.putText(velocity_img, str(velocity), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    state_img = np.zeros((subwindow_height, subwindow_width, 3), dtype=np.uint8)
    cv2.putText(state_img, state, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    movement_img = np.zeros((subwindow_height, subwindow_width, 3), dtype=np.uint8)
    cv2.putText(movement_img, movement, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    obstacles_img = np.zeros((subwindow_height, subwindow_width, 3), dtype=np.uint8)
    cv2.putText(obstacles_img, str(obstacles), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    frame = cv2.resize(frame, (subwindow_width, subwindow_height))
    blue = cv2.resize(blue, (subwindow_width, subwindow_height))
    lines = cv2.resize(lines, (subwindow_width, subwindow_height))

    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    if len(blue.shape) == 2:
        blue = cv2.cvtColor(blue, cv2.COLOR_GRAY2BGR)
    if len(lines.shape) == 2:
        lines = cv2.cvtColor(lines, cv2.COLOR_GRAY2BGR)


    videos1 = np.hstack((frame, blue, lines))
    videos2 = np.hstack((velocity_img, movement_img, obstacles_img))
    videos = np.vstack((videos1, videos2))

    cv2.imshow("Parameters", videos)

def main():
    global state
    state = "Avanzando"
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
            
        
        displayInterface(frame, blue, lines)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
