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
        else:
            print("porpprrorpo")
        
        # print ("hello " + str(ids[i][0]))
        # # Get the center coordinates of the marker
        # cX = int(corners[i][0][:, 0].mean())
        # cY = int(corners[i][0][:, 1].mean())
        # string1 = str(cX) + "/" + str(cY)
        # print(string1)

        # string = str(ids[i][0]) + "," + extra

        # # Draw the ID on the frame
        # cv2.putText(frame, string, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
# print(str(myCoordsX))
# print(str(myCoordsY))

# print(str(hisCoordsX))
# print(str(hisCoordsY))

# print(str(baseCoordsX))
# print(str(baseCoordsY))

# print(str(endCoordsX))
# print(str(endCoordsY))
myCoordsX = myCoordsX / 700 *1500
myCoordsY = myCoordsY / 700 *1500

hisCoordsX = hisCoordsX/ 700 *1500
hisCoordsY = hisCoordsY / 700 *1500

distX = hisCoordsX - myCoordsX
print(str(distX))

distY = hisCoordsY - myCoordsY
print(str(distY))

# cv2.imshow('Frame', frame)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


capture.release()

portIp = "127.0.0.1"
gobPort = 3001



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def Stop(ip, port):
    print("stopping")
    sock.sendto(bytes("0;" "0", "utf-8"), (ip, port))
    

def TurnRight(ip, port):
    print("turning right")
    sock.sendto(bytes("50;" "-50", "utf-8"), (ip, port))


def TurnLeft(ip, port):
    print("turning left")
    sock.sendto(bytes("-50;" "50", "utf-8"), (ip, port))
    


def Forward(ip, port):
    print("going forw")
    sock.sendto(bytes("100;" "100", "utf-8"), (ip, port))

def Backward(ip, port):
    print("going backw")
    sock.sendto(bytes("-100;" "-100", "utf-8"), (ip, port))

def TurnRightDegrees(ip, port, deg):
    print("turning right for " + str(deg) + " degrees")
    timer = deg / 360 * 1.96666555555555
    sock.sendto(bytes("50;" "-50", "utf-8"), (ip, port))
    time.sleep(timer)
    sock.sendto(bytes("0;" "0", "utf-8"), (ip, port))
    time.sleep(0.1)

def ForwardMm(ip, port, mms):
    print("going forward for " + str(mms) + " millimeters")
    timer = mms / 290
    sock.sendto(bytes("50;" "50", "utf-8"), (ip, port))
    time.sleep(timer)
    # Stop(ip, port)
    # time.sleep(0.01)
    # sock.sendto(bytes("-50;" "-50", "utf-8"), (ip, port))
    # time.sleep(0.1)
    Stop(ip, port)
    time.sleep(1)

degsToTurn = 0
distanceToTravel = 0

temp1 = distY / distX
degsToTurn = math.atan(temp1)
degsToTurn = math.degrees(degsToTurn)
if distX > 0 and distY > 0:
    degsToTurn += 0
elif distX > 0 and distY < 0:
    degsToTurn += 360
elif distX < 0 and distY > 0:
    degsToTurn += 180
elif distX < 0 and distY < 0:
    degsToTurn += 180

temp2 = distX ** 2
temp3 = distY ** 2
temp4 = temp2 + temp3
distanceToTravel = math.sqrt(temp4)

print(str(degsToTurn) + "   " + str(distanceToTravel))
TurnRightDegrees (portIp, gobPort, degsToTurn)
ForwardMm(portIp, gobPort, distanceToTravel)
Stop(portIp, gobPort)



sock.close()

