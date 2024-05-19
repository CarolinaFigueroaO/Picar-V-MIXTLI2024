import cv2
import numpy as np


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
    return mask

def getArea(frame):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 0])
    upper = np.array([179, 255, 100])
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def analyzeFrame(frame):
    mask = getArea(frame)
    
    # Encuentra contornos en la máscara
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Calcula el centroide promedio de los contornos
        cx_total = 0
        cy_total = 0
        total_area = 0
        
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                area = cv2.contourArea(contour)
                
                cx_total += cx * area
                cy_total += cy * area
                total_area += area
        
        if total_area != 0:
            avg_cx = cx_total / total_area
            avg_cy = cy_total / total_area
            
            # Divide la imagen en tres partes: izquierda, centro y derecha
            height, width = frame.shape[:2]
            left_boundary = width / 3
            right_boundary = 2 * width / 3
            
            if avg_cx < left_boundary+80:
                print("Girar a la izquierda")
            elif avg_cx > right_boundary-80:
                print("Girar a la derecha")
            else:
                print("Adelante")
        else:
            print("No se detecta área negra")
    else:
        print("No se detecta área negra")

    return mask


def main():
    # Suponiendo que estás capturando video desde una cámara
    cap = cv2.VideoCapture(0)
    createTrackbars()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = brightnessAjustment(frame)
        mask = analyzeFrame(frame)
        
        # Muestra el frame y la máscara para depuración
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
