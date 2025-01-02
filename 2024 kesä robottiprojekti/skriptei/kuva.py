import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np


capture = cv2.VideoCapture("http://localhost:8080")
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
        
        print ("hello " + str(ids[i][0]))
        # Get the center coordinates of the marker
        cX = int(corners[i][0][:, 0].mean())
        cY = int(corners[i][0][:, 1].mean())
        string1 = str(cX) + "/" + str(cY)
        print(string1)

        string = str(ids[i][0]) + "," + extra

        # Draw the ID on the frame
        cv2.putText(frame, string, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


# Convert the frame to the HSV color space
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Define HSV range for the color red (modify these ranges to match your colored ball)
lower_magenta = np.array([140, 100, 100])
upper_magenta = np.array([160, 255, 255])

lower_green = np.array([50, 100, 100])
upper_green = np.array([70, 255, 255])
#nää on jotain hsv arvoja

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
        cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
        cv2.putText(frame, f"{color_name} center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(frame, f"({cX}, {cY})", (cX + 20, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

# Process and draw contours for each color
process_contours(contours_magenta, frame, "Magenta")
process_contours(contours_green, frame, "Green")


cv2.imshow('Frame', frame)
cv2.waitKey(0)
cv2.destroyAllWindows()


# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# while True:
#     time.sleep(1)
#     sock.sendto(bytes("100;" "-100", "utf-8"), ("127.0.0.1", 3001))
#     time.sleep(1)
#     sock.sendto(bytes("0;" "0", "utf-8"), ("127.0.0.1", 3001))




