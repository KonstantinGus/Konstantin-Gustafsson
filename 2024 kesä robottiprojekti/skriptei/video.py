import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math


capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def posCheck(id): #tunnistaa missä aruco marker on ja mikä sen kulma on
    global corners, ids
    coords = None
    angle = None
    
    if ids is not None and corners is not None:
        for i in range(len(ids)):
            if ids[i][0] == id:
                coords = (corners[i][0][:, 0].mean(), corners[i][0][:, 1].mean())
                corner = corners[i][0]
                vector = corner[3] - corner[2] #joskus kamerasta liittyen pitää käyttää eri kulmia, jos robotti kääntyy 180 pieleen, koita vaihtaa päittäin 2-3 -> 3-2
                angle = math.atan2(vector[1], vector[0])
                break
    return coords, angle
def Distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

pointI = None
pointJ = None

# pointI = posCheck(48)[0]
# pointJ = posCheck(49)[0]
# distance123 = Distance(pointI, pointJ)
# print(Distance)


while True:
    ret, frame = capture.read()



    # Initialize Aruco dictionary
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)

    # Initialize Aruco parameters
    parameters = aruco.DetectorParameters()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect Aruco markers in the frame
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

    if ids is not None:
        for i in range(len(ids)):
            if ids[i][0] == 2:
                extra = "goblin"
            elif ids[i][0] == 3:
                extra = "friend"
            else:
                extra = ""
            
            #print ("hello " + str(ids[i][0]))
            # Get the center coordinates of the marker
            cX = int(corners[i][0][:, 0].mean())
            cY = int(corners[i][0][:, 1].mean())
            string1 = str(cX) + "/" + str(cY)
            #print(string1)

            string = str(ids[i][0]) + "," + extra

            # Draw the ID on the frame
            cv2.putText(frame, string, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define HSV range for the color red (modify these ranges to match your colored ball)
    # lower_magenta = np.array([140, 100, 100])
    # upper_magenta = np.array([160, 255, 255])

    # lower_green = np.array([50, 100, 100])
    # upper_green = np.array([70, 255, 255])
    # #nää on jotain hsv arvoja

    lower_magenta = np.array([170, 150, 150])
    upper_magenta = np.array([180, 255, 255])
    # lower_green = np.array([28, 150, 200])
    # upper_green = np.array([32, 255, 255])
    lower_green = np.array([25, 100, 150])  # More yellowish and less saturated/bright
    upper_green = np.array([40, 255, 255])  # More gr



    mask_magenta  = cv2.inRange(hsv, lower_magenta, upper_magenta)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)


    # Find contours in the masks
    contours_magenta, _ = cv2.findContours(mask_magenta, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Function to process contours
    def process_contours(contours, frame, color_name):
        for contour in contours:
            # Calculate the moments of the contour to find the center
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0

            # Draw the contour and the center of the shape on the frame
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.circle(frame, (cX, cY), 2, (255, 255, 255), -1)
            cv2.putText(frame, f"{color_name} center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f"({cX}, {cY})", (cX + 20, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Process and draw contours for each color
    process_contours(contours_magenta, frame, "Magenta")
    process_contours(contours_green, frame, "Green")


    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
capture.release()
cv2.destroyAllWindows()




# while True:
#     time.sleep(1)
#     sock.sendto(bytes("100;" "-100", "utf-8"), ("127.0.0.1", 3001))
#     time.sleep(1)
#     sock.sendto(bytes("0;" "0", "utf-8"), ("127.0.0.1", 3001))




