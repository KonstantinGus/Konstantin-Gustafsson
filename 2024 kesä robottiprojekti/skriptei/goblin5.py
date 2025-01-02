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

capture.release()

portIp = "127.0.0.1"
gobPort = 3001



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2 on goblin
# 3 friend
# 47 on 00
# 48 on 1500/1500
#50 on oma maali

myCoordsX = 0 # decl some variables turhaa kai pythonissa
myCoordsY = 0
hisCoordsX = 0
hisCoordsY = 0
baseCoordsX = 0
baseCoordsY = 0
endCoordsX = 0
endCoordsY = 0
goalCoordsX = 0
goalCoordsY = 0

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
            print(f"Angle: {angle:.2f} degrees")

                            
        elif ids[i][0] == 3:
            extra = "friend"
            hisCoordsX = int(corners[i][0][:, 0].mean())
            hisCoordsY = int(corners[i][0][:, 1].mean())
                            
        elif ids[i][0]== 47:
            extra = ""
            baseCoordsX = int(corners[i][0][:, 0].mean())
            baseCoordsY = int(corners[i][0][:, 1].mean())
            
        elif ids[i][0]== 48:
            extra = ""
            endCoordsX = int(corners[i][0][:, 0].mean())
            
            endCoordsY = int(corners[i][0][:, 1].mean())
        elif ids[i][0]== 50:
            extra = ""
            goalCoordsX = int(corners[i][0][:, 0].mean())
            
            goalCoordsY = int(corners[i][0][:, 1].mean())



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


def BilliardManouver(myX, myY, ballX, ballY, goalX, goalY):
    #ratkaisee mihin robon pitää mennä, että maali on suoraan kohteen takana
    dx = goalX - ballX
    dy = goalY - ballY
    t = ((myX - ballX) * dx + (myY - ballY) * dy) / (dx**2 + dy**2)
    x = ballX + t * dx
    y = ballY + t * dy
    angle = math.degrees(math.atan(dx / dy))

    return x, y, angle

def CoordsToMms(coords):
    return coords / 700 * 1500




posX, posY, posA = BilliardManouver(myCoordsX, myCoordsY, hisCoordsX, hisCoordsY, goalCoordsX, goalCoordsY)   
print(str(posX) +"--" +str(posY) +"--"+str(posA))  

degs1 = math.degrees(math.atan2((posY - myCoordsY), (posX - myCoordsX),)) - angle
#degs1 = math.degrees(math.atan( (posY - myCoordsY)/ (posX - myCoordsX))) - angle
#degs1 = math.degrees(math.atan( (myCoordsY -posY)/ ( myCoordsX- posX))) - angle



# while degs1 > 180:
#     degs1 = degs1 - 360
# while degs1 < -180:
#     degs1 = degs1 + 360
dist1 = math.sqrt((posX - myCoordsX)**2 + (posY - myCoordsY)**2)
dist1 = CoordsToMms(dist1)
time.sleep(0.5)

TurnDegrees(portIp, gobPort, degs1)
time.sleep(0.5)

ForwardMm(portIp, gobPort, dist1)
time.sleep(0.5)


#TurnDegrees(portIp, gobPort, 90)


sock.sendto(bytes("0;0", "utf-8"), (portIp, gobPort))
sock.close()