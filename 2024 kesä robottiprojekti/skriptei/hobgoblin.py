import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math


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


def CapFrame(): #voiskohan nää lykkää tänne
    global ret, ids, rejectedImgPoints, corners, capture
    capture = cv2.VideoCapture("http://localhost:8080")
    ret, frame = capture.read()
    capture.release()

    parameters = aruco.DetectorParameters()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

myCoords = (0, 0)
hisCoords = (0, 0)
myAngle = 0

#id cheat sheet:
# 2 on goblin
# 3 friend
# 47 on 00
# 48 on 1500/1500
#50 on oma maali


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


#working lane 300/300, 460/460, nää vois tarkistaa
pointA = (300, 300)
pointB = (460, 460)


for i in range(10):
    print(i+1)
    CapFrame()
    myCoords, myAngle = posCheck(2)
    hisCoords = posCheck(0)[0]
    angleToTurn, distToTravel = WhereTo(myCoords, myAngle, hisCoords)
    TurnDegrees(portIp, gobPort, angleToTurn)
    ForwardMm(portIp, gobPort, distToTravel)












sock.sendto(bytes("0;0", "utf-8"), (portIp, gobPort))
capture.release()
sock.close()
