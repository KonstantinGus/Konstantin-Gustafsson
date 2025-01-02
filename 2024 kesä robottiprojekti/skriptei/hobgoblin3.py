import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math
import random


portIp = "127.0.0.1"
gobPort = 3001
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# capture = cv2.VideoCapture("http://localhost:8080")
# ret, frame = capture.read()
# capture.release()

# parameters = aruco.DetectorParameters()
# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# detector = aruco.ArucoDetector(aruco_dict, parameters)
# corners, ids, rejectedImgPoints = detector.detectMarkers(gray)


lower_magenta = np.array([140, 100, 100])
upper_magenta = np.array([160, 255, 255])
lower_green = np.array([50, 100, 100])
upper_green = np.array([70, 255, 255])

def CapFrame(): #voiskohan nää lykkää tänne
    global ret, ids, rejectedImgPoints, corners, capture, contours_green, contours_magenta, magenta_centers, green_centers
    ret = ids = rejectedImgPoints = corners = capture = contours_green = contours_magenta = magenta_centers = green_centers = None

    capture = cv2.VideoCapture("http://localhost:8080")
    ret, frame = capture.read()
    capture.release()

    parameters = aruco.DetectorParameters()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_magenta = cv2.inRange(hsv, lower_magenta, upper_magenta)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    contours_magenta, _ = cv2.findContours(mask_magenta, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    magenta_centers = get_contour_centers(contours_magenta)
    green_centers = get_contour_centers(contours_green)

myCoords = (0, 0)
hisCoords = (0, 0)
myAngle = 0

#id cheat sheet:
# 2 on goblin
# 3 friend
# 47 on 00
# 48 on 1500/1500
#50 on oma maali
#0 on nuolinäppäinvihiu
#1 on wasdvihu

def get_contour_centers(contours): #tätä tarvitaan palloihin
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centers.append((cX, cY))
    return centers

def posCheck(id):
    coords = None
    angle = None
    for i in range(len(ids)):
        if ids[i][0] == id:
            coords = (corners[i][0][:, 0].mean(), corners[i][0][:, 1].mean())
            corner = corners[i][0]
            vector = corner[2] - corner[3] # otetaan eri cornereista kulma nii ei tarvii lisätä 90 astetta myöhemmin
            angle = (math.atan2(vector[1], vector[0]))
            break
    return coords, angle
    

def SendIt(lv, rv): #leftvalue, rightvalue
    command = f"{lv};{rv}"
    sock.sendto(command.encode(), (portIp, gobPort))
    
def isPointing(coords, angle, targetCoords, threshold): #turhahko funktio, pointingAngle monikäyttösempi
    thresholdRads = np.radians(threshold)#tolerance in degs
    vector = np.array(targetCoords) - np.array(coords)
    vectorAngle = np.arctan2(vector[1], vector[0])
    #vectorAngle += np.pi /2 #tää on nyt turha
    angleDiff = np.abs(angle - vectorAngle)
    angleDiff = np.abs((angleDiff + np.pi) % (2 * np.pi) - np.pi)
    pointing = abs(angleDiff) < thresholdRads
    return pointing

def pointingAngle(coords, angle, targetCoords):
    vector = np.array(targetCoords) - np.array(coords)
    vectorAngle = np.arctan2(vector[1], vector[0])
    vectorAngle += np.pi /2
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


#huom! funktion sisällä time.sleep, ongelma tulevaisuudessa?
def TurnDegrees(ip, port, deg): #+ left, - right
    print("turning for " + str(deg) + " degrees")
    tempDeg = abs(deg)
    timer = tempDeg / 360 * 1.96666555555555
    if deg > 0:
        sock.sendto(bytes("-50;50", "utf-8"), (ip, port))
    elif deg < 0:
        sock.sendto(bytes("50;-50", "utf-8"), (ip, port))
    time.sleep(timer)
    sock.sendto(bytes("0;0", "utf-8"), (ip, port))
    sock.sendto(bytes("1;1", "utf-8"), (ip, port)) #mahd pysäyttää, ei tarpeen fyys ympr?
    sock.sendto(bytes("-1;-1", "utf-8"), (ip, port))
    sock.sendto(bytes("0;0", "utf-8"), (ip, port))
    time.sleep(0.1)
def ForwardMm(ip, port, mms): #+ eteen, -taakse
    print("going forward for " + str(mms) + " millimeters")
    tempMms=abs(mms)
    timer = tempMms / 290
    if mms > 0:
        sock.sendto(bytes("50;50", "utf-8"), (ip, port))
    if mms < 0:
        sock.sendto(bytes("-50;-50", "utf-8"), (ip, port))
    time.sleep(timer)
    sock.sendto(bytes("0;0", "utf-8"), (ip, port))

    time.sleep(0.1)
def CoordsToMms(coords):
    return coords / 700 * 1500

def Distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def WhereTo(coords, angle, target):
    angle1 = pointingAngle(coords, angle, target)
    dist1 = CoordsToMms(Distance(coords, target))
    return angle1, dist1


def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def IsItInside(target, a, b, c, d):
    x, y = target
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d

    # Vectors AB, AD, and AM
    AB = (bx - ax, by - ay)
    AD = (dx - ax, dy - ay)
    AM = (x - ax, y - ay)
    
    # Dot products
    AM_AB = dot_product(AM, AB)
    AB_AB = dot_product(AB, AB)
    AM_AD = dot_product(AM, AD)
    AD_AD = dot_product(AD, AD)
    
    # Condition checks for AB and AD
    condition1 = 0 < AM_AB < AB_AB
    condition2 = 0 < AM_AD < AD_AD

    # Repeat for vectors BC, CD, and CM to check the other two sides
    BC = (cx - bx, cy - by)
    CD = (dx - cx, dy - cy)
    BM = (x - bx, y - by)
    CM = (x - cx, y - cy)
    
    # Dot products for BC and CD
    BM_BC = dot_product(BM, BC)
    BC_BC = dot_product(BC, BC)
    CM_CD = dot_product(CM, CD)
    CD_CD = dot_product(CD, CD)
    
    # Condition checks for BC and CD
    condition3 = 0 < BM_BC < BC_BC
    condition4 = 0 < CM_CD < CD_CD
    
    return condition1 and condition2 and condition3 and condition4

def BilliardManeuver(my_pos = tuple, ball_pos =tuple, goal_pos =tuple):
    # Solve where the robot needs to go so the goal is directly behind the target
    myX = my_pos[0]
    myY = my_pos[1]
    ballX = ball_pos[0]
    ballY = ball_pos[1]
    goalX = goal_pos[0]
    goalY = goal_pos[1]

    
    dx = goalX - ballX
    dy = goalY - ballY
    
    t = ((myX - ballX) * dx + (myY - ballY) * dy) / (dx**2 + dy**2)
    
    x = ballX + t * dx
    y = ballY + t * dy
    angle = math.degrees(math.atan2(dy, dx))
    
    return (x, y), angle

#working lane 300/300, 460/460, nää vois tarkistaa, on nyt pielessä, mutta testaillaan silti
#AB, keskilinja, A1B1 omat tolpat, A2B2 vihun tolpat
pointA = (300, 300)
pointB = (460, 460)
pointA1 = (500, 100)
pointB1 = (650, 250)

pointA2 = (80, 475)
pointB2 =(230, 650)

# point123 = (470, 250)

# print(IsItInside(point123,pointA, pointA1, pointB1, pointB ))

#game_time pitäisi käyttää, jotte goblin etsisi palloja koko peliajan, vaikka hetkellisesti all_centers ois False
game_time = 180 # 180 sekuntia (30 sekuntia extra peliajasta, jos jotain käy)

while True:
    CapFrame()
    myCoords, myAngle = posCheck(2)
    angle1 = WhereTo(myCoords, myAngle, pointA)[0]
    dist1 = WhereTo(myCoords, myAngle, pointA)[1]

    TurnDegrees(portIp, gobPort, angle1)
    ForwardMm(portIp, gobPort, dist1)

    CapFrame()
    myCoords, myAngle = posCheck(2)
    TurnDegrees(portIp, gobPort, WhereTo(myCoords, myAngle, pointB)[0])
    ForwardMm(portIp, gobPort, WhereTo(myCoords, myAngle, pointB)[1])

    CapFrame()
    myCoords, myAngle = posCheck(2)



    betterGreenCenters = []
    for center in green_centers:
        if IsItInside(center, pointA, pointA1, pointB1, pointB):
            betterGreenCenters.append(center)

    green_centers = betterGreenCenters

    betterMagentaCenters = []
    for center in magenta_centers:
        if IsItInside(center, pointA, pointA2, pointB2, pointB):
            betterMagentaCenters.append(center)

    magenta_centers = betterMagentaCenters


    goalPos2 = None
    targetBall = None
    all_centers = []
    all_centers = green_centers + magenta_centers

# Yritin tehdä loopia, jossa odotetaan, jos uusia palloja ilmestyisi
    if not all_centers:
        print("No balls detected")
        time.sleep(5) # 5sec nopeaa testausta varten
        # miten tarkistetaan uudelleen all_centers kuvasta?
        if not all_centers:
            print("Still no balls detected")
            targetBall = None
        else:
            print("Sike")
            continue

    else:
        targetBall = random.choice(all_centers)
        if targetBall in green_centers:
            goalPos2 = posCheck(47)[0]
        elif targetBall in magenta_centers:
            goalPos2 = posCheck(50)[0]

    if targetBall == None:
        print("all done, boss")
        break
    goalPos2 = posCheck(50)[0]
    print(targetBall)
    tempTarg = BilliardManeuver(myCoords, targetBall, goalPos2)[0]

    TurnDegrees(portIp, gobPort, WhereTo(myCoords, myAngle, tempTarg)[0])
    ForwardMm(portIp, gobPort, WhereTo(myCoords, myAngle, tempTarg)[1])


    CapFrame()
    myCoords, myAngle = posCheck(2)

    TurnDegrees(portIp, gobPort, WhereTo(myCoords, myAngle, targetBall)[0])
    ForwardMm(portIp, gobPort, (WhereTo(myCoords, myAngle, goalPos2)[1]+50))



sock.sendto(bytes("0;0", "utf-8"), (portIp, gobPort))
capture.release()
sock.close()


