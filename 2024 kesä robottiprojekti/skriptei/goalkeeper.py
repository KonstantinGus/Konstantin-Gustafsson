import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math
import threading

portIp = "127.0.0.1"
gobPort = 3001
frndPort = 3002
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

lower_magenta = np.array([140, 100, 100])
upper_magenta = np.array([160, 255, 255])
lower_green = np.array([50, 100, 100])
upper_green = np.array([70, 255, 255])

ret = ids = rejectedImgPoints = corners = contours_green = contours_magenta = magenta_centers = green_centers = None
lock_the_frame = threading.Lock()
update_frame = threading.Event()

start_pos = None
goal_pos = None

def CapFrame():
    global ret, ids, rejectedImgPoints, corners, contours_green, contours_magenta, magenta_centers, green_centers, start_pos, goal_pos
    capture = cv2.VideoCapture("http://localhost:8080")
    while True:
        ret, frame = capture.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            parameters = aruco.DetectorParameters()
            detector = aruco.ArucoDetector(aruco_dict, parameters)
            corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask_magenta = cv2.inRange(hsv, lower_magenta, upper_magenta)
            mask_green = cv2.inRange(hsv, lower_green, upper_green)

            contours_magenta, _ = cv2.findContours(mask_magenta, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            magenta_centers = get_contour_centers(contours_magenta)
            green_centers = get_contour_centers(contours_green)

            # Capture initial positions
            if start_pos is None or goal_pos is None:
                friendCoords, _ = posCheck(3)
                goalCoords, _ = posCheck(47)
                if friendCoords is not None and goalCoords is not None:
                    start_pos = friendCoords
                    goal_pos = goalCoords

        with lock_the_frame:
            update_frame.set()
        time.sleep(0.1)
    capture.release()

def get_contour_centers(contours): #tätä tarvitaan palloihin
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centers.append((cX, cY))
    return centers

#id cheat sheet:
# 2 on goblin
# 3 friend
# 47 on 00
# 48 on 1500/1500
#50 on oma maali
#0 on nuolinäppäinvihiu
#1 on wasdvihu

def posCheck(id):
    global corners, ids
    coords = None
    angle = None
    with lock_the_frame:
        if ids is not None and corners is not None:
            for i in range(len(ids)):
                if ids[i][0] == id:
                    coords = (corners[i][0][:, 0].mean(), corners[i][0][:, 1].mean())
                    corner = corners[i][0]
                    vector = corner[2] - corner[3]
                    angle = math.atan2(vector[1], vector[0])
                    break
    return coords, angle

def SendIt(lv, rv): #leftvalue, rightvalue
    command = f"{lv};{rv}"
    sock.sendto(command.encode(), (portIp, gobPort))

def SendItFriend(lv, rv): #leftvalue, rightvalue
    command = f"{lv};{rv}"
    sock.sendto(command.encode(), (portIp, frndPort))

def pointingAngle(coords, angle, targetCoords):
    vector = np.array(targetCoords) - np.array(coords)
    vectorAngle = np.arctan2(vector[1], vector[0])
    vectorAngle += np.pi / 2
    angleDiff = (angle - vectorAngle)
    angleDiff = ((angleDiff + np.pi) % (2 * np.pi) - np.pi)
    return np.degrees(angleDiff)

def Turn(speed, dir =str): #dir ccw, tai cw, clockwise, counterclock
    if dir == "cw":
        SendIt(-speed, speed)
    elif dir == "ccw":
        SendIt(speed,-speed)
    else:
        SendIt (0,0)
        print("anna toinen")

def TurnFriend(speed, dir =str): #dir ccw, tai cw, clockwise, counterclock
    if dir == "cw":
        SendItFriend(-speed, speed)
    elif dir == "ccw":
        SendItFriend(speed,-speed)
    else:
        SendItFriend (0,0)
        print("anna toinen")

def StopFriend():
    SendItFriend(0, 0)

#working lane 300/300, 460/460, nää vois tarkistaa, on nyt pielessä, mutta testaillaan silti
#AB, keskilinja, A1B1 omat tolpat, A2B2 vihun tolpat
pointA = (300, 300)
pointB = (460, 460)
pointA1 = (500, 100)
pointB1 = (650, 250)

pointA2 = (80, 475)
pointB2 = (230, 650)

angle2 = 0
angleFrnd = 0

frame_capture_thread = threading.Thread(target=CapFrame, daemon=True)
frame_capture_thread.start()

game_time = 60     # 180 sekuntia (virallinen peliaika 2 min 30 sec, 30 sec extra peliajasta, jos jotain käy)
start_time = time.time()

spd1 = 100
spd2 = 100

while time.time() - start_time < game_time:
    update_frame.wait()
    update_frame.clear()

    myCoords, myAngle = posCheck(2)
    friendCoords, friendAngle = posCheck(3)
    ownGoalCoords, ownGoalAngle = posCheck(47)

    if myCoords is None or myAngle is None or friendCoords is None or friendAngle is None or start_pos is None or goal_pos is None:
        continue

    goblin_close = np.linalg.norm(np.array(myCoords) - np.array(ownGoalCoords))
    too_close = 50 #goblinin etäisyys maalista

    target_pos = start_pos if goblin_close < too_close else goal_pos

    target_angl = pointingAngle(friendCoords, friendAngle, target_pos)

    if abs(target_angl) > 10:
        if target_angl > 0:
            TurnFriend(spd1, "ccw")
        else:
            TurnFriend(spd1, "cw")
    else:
        SendItFriend(spd1, spd1)

    time.sleep(0.1)

sock.sendto(bytes("0;0", "utf-8"), (portIp, gobPort))
sock.sendto(bytes("0;0", "utf-8"), (portIp, frndPort))
sock.close()
