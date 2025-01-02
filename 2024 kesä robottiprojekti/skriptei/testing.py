import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math
import random
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

def CapFrame():
    global ret, ids, rejectedImgPoints, corners, contours_green, contours_magenta, magenta_centers, green_centers
    while True:
        capture = cv2.VideoCapture("http://localhost:8080")
        ret, frame = capture.read()
        capture.release()

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
        
        with lock_the_frame:
            update_frame.set()
        time.sleep(0.1)

myCoords = (0, 0)
hisCoords = (0, 0)
myAngle = 0

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

def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def IsItInside(target, a, b, c, d):
    x, y = target
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d

    AB = (bx - ax, by - ay)
    AD = (dx - ax, dy - ay)
    AM = (x - ax, y - ay)
    
    AM_AB = dot_product(AM, AB)
    AB_AB = dot_product(AB, AB)
    AM_AD = dot_product(AM, AD)
    AD_AD = dot_product(AD, AD)
    
    condition1 = 0 < AM_AB < AB_AB
    condition2 = 0 < AM_AD < AD_AD

    BC = (cx - bx, cy - by)
    CD = (dx - cx, dy - cy)
    BM = (x - bx, y - by)
    CM = (x - cx, y - cy)
    
    BM_BC = dot_product(BM, BC)
    BC_BC = dot_product(BC, BC)
    CM_CD = dot_product(CM, CD)
    CD_CD = dot_product(CD, CD)
    
    condition3 = 0 < BM_BC < BC_BC
    condition4 = 0 < CM_CD < CD_CD
    
    return condition1 and condition2 and condition3 and condition4

#working lane 300/300, 460/460, nää vois tarkistaa, on nyt pielessä, mutta testaillaan silti
#AB, keskilinja, A1B1 omat tolpat, A2B2 vihun tolpat
pointA = (300, 300)
pointB = (460, 460)
pointA1 = (500, 100)
pointB1 = (650, 250)

pointA2 = (80, 475)
pointB2 = (230, 650)

# point123 = (470, 250)

# print(IsItInside(point123,pointA, pointA1, pointB1, pointB ))

angle2 = 0
angleFrnd = 0

frame_capture_thread = threading.Thread(target=CapFrame, daemon=True)
frame_capture_thread.start()

game_time = 180     # 180 sekuntia (virallinen peliaika 2 min 30 sec, 30 sec extra peliajasta, jos jotain käy)
start_time = time.time()

spd1 = 100
spd2 = 100

while time.time() - start_time < game_time:
    update_frame.wait()
    update_frame.clear()
    dir = ""
    spd1 = int(abs(angle2) / 1.8 * 1.6)

    dir2 =""
    spd2 = int(abs(angleFrnd) / 1.8 * 1.6)

    pos1 = posCheck(2)[0]
    angle1 = posCheck(2)[1]
    tar1 = posCheck(0)[0]
    angle2 = pointingAngle(pos1, angle1, tar1)
    angleFrnd = pointingAngle(posCheck(3)[0], posCheck(3)[1], tar1)

    myCoords, myAngle = posCheck(2)
    if myCoords is None or myAngle is None:
        continue

    with lock_the_frame:
        betterGreenCenters = [center for center in green_centers if IsItInside(center, pointA, pointA1, pointB1, pointB)]
        betterMagentaCenters = [center for center in magenta_centers if IsItInside(center, pointA, pointA2, pointB2, pointB)]
        all_centers = betterGreenCenters + betterMagentaCenters

    """if not all_centers:
        print("No balls detected")
    else:
        #testaukseen, tulostaa pallojen sijainnit
        print(f"Better Green Centers: {betterGreenCenters}")
        print(f"Better Magenta Centers: {betterMagentaCenters}")

    update_frame.wait()
    update_frame.clear()"""

    if spd1 >100: # tän lisäsin ku lisäsin 1.6, kosk 100 on maksimi
        spd1 = 100
    if spd1 < 20: # speedi oli välillä hidas
        spd1 = 20
    if angle2 < 0:
        dir1 = "ccw"
    elif angle2 > 0:
        dir1 = "cw"
    if abs(angle2) < 10:
        SendIt(0,0)
    else:
        Turn(spd1, dir1)
        
    if spd2 >100: # tän lisäsin ku lisäsin 1.6, kosk 100 on maksimi
        spd2 = 100
    if spd2 < 20: # speedi oli välillä hidas
        spd2 = 20
    if angleFrnd < 0:
        dir2= "ccw"
    elif angleFrnd > 0:
        dir2 = "cw"
    if abs(angleFrnd) < 10:
        SendItFriend(0,0)
    else:
        TurnFriend(spd2, dir2)

    time.sleep(0.01)

sock.sendto(bytes("0;0", "utf-8"), (portIp, gobPort))
sock.sendto(bytes("0;0", "utf-8"), (portIp, frndPort))
sock.close()