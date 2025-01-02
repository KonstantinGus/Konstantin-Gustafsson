import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math

capture = cv2.VideoCapture("http://localhost:8080")
ret, frame = capture.read()

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
parameters = aruco.DetectorParameters()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
detector = aruco.ArucoDetector(aruco_dict, parameters)
corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

# 2 on goblin
# 3 friend
# 47 on 00
# 48 on 1500/1500

myCoordsX = 0
myCoordsY = 0

hisCoordsX = 0
hisCoordsY = 0

baseCoordsX = 0
baseCoordsY = 0

endCoordsX = 0
endCoordsY = 0

distX = 0
distY = 0

for i in range(len(ids)):
    if ids[i][0] == 2:
        extra = "goblin"
        myCoordsX = int(corners[i][0][:, 0].mean())
        myCoordsY = int(corners[i][0][:, 1].mean())

        corner = corners[i][0]
        vector = corner[1] - corner[0]
        angle = math.degrees(math.atan2(vector[1], vector[0]))
        angle -= 90
        print(f"Angle: {angle:.2f} degrees")

    elif ids[i][0] == 3:
        extra = "friend"
        hisCoordsX = int(corners[i][0][:, 0].mean())
        hisCoordsY = int(corners[i][0][:, 1].mean())
        

    elif ids[i][0] == 47:
        extra = ""
        baseCoordsX = int(corners[i][0][:, 0].mean())
        baseCoordsY = int(corners[i][0][:, 1].mean())

    elif ids[i][0] == 48:
        extra = ""
        endCoordsX = int(corners[i][0][:, 0].mean())
        endCoordsY = int(corners[i][0][:, 1].mean())

myCoordsX = myCoordsX / 700 * 1500
myCoordsY = myCoordsY / 700 * 1500

# Detect balls
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

lower_magenta = np.array([140, 100, 100])
upper_magenta = np.array([160, 255, 255])
lower_green = np.array([50, 100, 100])
upper_green = np.array([70, 255, 255])

mask_magenta = cv2.inRange(hsv, lower_magenta, upper_magenta)
mask_green = cv2.inRange(hsv, lower_green, upper_green)

contours_magenta, _ = cv2.findContours(mask_magenta, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

def get_contour_centers(contours):
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centers.append((cX, cY))
    return centers

magenta_centers = get_contour_centers(contours_magenta)
green_centers = get_contour_centers(contours_green)

# Find the closest green ball to the Aruco marker with ID 2
closest_center = None
if green_centers and 2 in ids:
    min_distance = float('inf')
    marker_center = (myCoordsX, myCoordsY)
    for center in green_centers:
        cX, cY = center
        cX = cX / 700 * 1500
        cY = cY / 700 * 1500
        distance = np.sqrt((marker_center[0] - cX) ** 2 + (marker_center[1] - cY) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_center = (cX, cY)

if closest_center:
    distX = closest_center[0] - myCoordsX
    distY = closest_center[1] - myCoordsY
    print(f"Closest Green Ball: {closest_center}, Distance: {min_distance:.2f} mm")

capture.release()

portIp = "127.0.0.1"
gobPort = 3001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def Stop(ip, port):
    print("stopping")
    sock.sendto(bytes("0;0", "utf-8"), (ip, port))

def TurnRight(ip, port):
    print("turning right")
    sock.sendto(bytes("50;-50", "utf-8"), (ip, port))

def TurnLeft(ip, port):
    print("turning left")
    sock.sendto(bytes("-50;50", "utf-8"), (ip, port))

def Forward(ip, port):
    print("going forward")
    sock.sendto(bytes("100;100", "utf-8"), (ip, port))

def Backward(ip, port):
    print("going backward")
    sock.sendto(bytes("-100;-100", "utf-8"), (ip, port))

def TurnRightDegrees(ip, port, deg):
    print("turning right for " + str(deg) + " degrees")
    timer = deg / 360 * 1.96666555555555
    sock.sendto(bytes("50;-50", "utf-8"), (ip, port))
    time.sleep(timer)
    sock.sendto(bytes("0;0", "utf-8"), (ip, port))
    time.sleep(0.1)

def ForwardMm(ip, port, mms):
    print("going forward for " + str(mms) + " millimeters")
    timer = mms / 290
    sock.sendto(bytes("50;50", "utf-8"), (ip, port))
    time.sleep(timer)
    Stop(ip, port)
    time.sleep(1)

# Implement the logic to move towards the detected ball
if closest_center:
    angle_to_turn = math.degrees(math.atan2(distY, distX)) - angle
    if angle_to_turn < 0:
        angle_to_turn += 360
    print(f"Turning by {angle_to_turn:.2f} degrees")
    TurnRightDegrees(portIp, gobPort, angle_to_turn)
    #ForwardMm(portIp, gobPort, min_distance)

sock.close()
