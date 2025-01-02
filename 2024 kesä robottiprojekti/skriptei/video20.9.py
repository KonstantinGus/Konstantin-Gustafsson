import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math

capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)


# Function to calculate the position and angle of an Aruco marker
def posCheck(id, corners, ids):  # Pass corners and ids explicitly
    coords = None
    angle = None
    
    if ids is not None and corners is not None:
        for i in range(len(ids)):
            if ids[i][0] == id:
                coords = (corners[i][0][:, 0].mean(), corners[i][0][:, 1].mean())
                corner = corners[i][0]
                vector = corner[3] - corner[2]  # Vector between two corners for angle
                angle = math.atan2(vector[1], vector[0])
                break
    return coords, angle

# Function to calculate distance between two points
def Distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

while True:
    ret, frame = capture.read()
    if not ret:
        continue  # Skip if frame is not available

    # Initialize Aruco dictionary and parameters
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
    parameters = aruco.DetectorParameters()
    
    # Convert the frame to grayscale for Aruco detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect Aruco markers in the frame
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
    # width = 640
    # height = 480

    # capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    # Check for specific markers 48 and 49 and calculate their positions
    if ids is not None:
        pointI = posCheck(48, corners, ids)[0]  # Position of marker 48
        pointJ = posCheck(49, corners, ids)[0]  # Position of marker 49
        pointT = posCheck(37, corners, ids)[0]
        pointR = posCheck(37, corners, ids)[0]
        print ("T:"+ str(pointT))
        print ("R:"+ str(pointR))

        # If both points are detected, calculate the distance
        if pointI is not None and pointJ is not None:
            distance123 = Distance(pointI, pointJ)
            print(f"Distance between marker 48 and 49: {distance123}")
    
        for i in range(len(ids)):
            extra = ""
            if ids[i][0] == 2:
                extra = "goblin"
            elif ids[i][0] == 3:
                extra = "friend"
            
            # Get the center coordinates of the marker
            cX = int(corners[i][0][:, 0].mean())
            cY = int(corners[i][0][:, 1].mean())
            string = str(ids[i][0]) + "," + extra

            # Draw the ID and extra information on the frame
            cv2.putText(frame, string, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define HSV range for the color magenta and green
    lower_magenta = np.array([170, 150, 150])
    upper_magenta = np.array([180, 255, 255])
    lower_green = np.array([25, 100, 150])
    upper_green = np.array([40, 255, 255])

    # lower_magenta = np.array([255, 255, 255])
    # upper_magenta = np.array([255, 255, 255])
    # lower_green = np.array([255, 255, 255])
    # upper_green = np.array([255, 255, 255])

    # Create masks for magenta and green
    mask_magenta = cv2.inRange(hsv, lower_magenta, upper_magenta)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Find contours in the masks
    contours_magenta, _ = cv2.findContours(mask_magenta, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Function to process contours and draw them
    def process_contours(contours, frame, color_name):
        for contour in contours:
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

    # Show the frame
    cv2.imshow('Frame', frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
capture.release()
cv2.destroyAllWindows()
