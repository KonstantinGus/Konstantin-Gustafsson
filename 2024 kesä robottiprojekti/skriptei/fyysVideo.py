import socket
import time
import cv2
import cv2.aruco as aruco
import threading
import numpy as np
import math



aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)

portIp = "192.168.137.179"
gobPort = 3000

# portIp = "127.0.0.1"
# gobPort = 3001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ret = ids = rejectedImgPoints = corners = contours_green = contours_magenta = magenta_centers = green_centers = None
lock_the_frame = threading.Lock()
update_frame = threading.Event()

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
        #print(dir)
    elif dir == "ccw":
        SendIt(speed,-speed)
        #print(dir)
    else:
        SendIt (0,0)
        #print("anna toinen")

def NormalizeSpeed(spd):
    if spd >100: #työntää takas rangelle jos menee yli 100
        spd = 100
    if spd < 20: #jos liian hidas
        spd = 20
    spd = int(spd) #jos floatti nii muuttaa intiks
    return spd

def TurnDirCheck(angle): #kattoo pitäskö kääntyä clockwise vai countercw
    dir =""
    if angle < 0:
        dir = "ccw"
    elif angle > 0:
        dir = "cw"
    return dir

def normalize_angle(angle):
    angle = (angle + 180) % 360 - 180
    return angle

def CapFrame():
    global ret, ids, rejectedImgPoints, corners, contours_green, contours_magenta, magenta_centers, green_centers
    while True:
        capture = cv2.VideoCapture(0)
        #capture = cv2.VideoCapture("http://localhost:8080")

        ret, frame = capture.read()
        capture.release()

        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            parameters = aruco.DetectorParameters()
            detector = aruco.ArucoDetector(aruco_dict, parameters)
            corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        
        with lock_the_frame:
            update_frame.set()
        time.sleep(0.001)


frame_capture_thread = threading.Thread(target=CapFrame, daemon=True)
frame_capture_thread.start()

game_time = 100
start_time = time.time()

goalAngle = -181
goalAngleRads = math.radians(goalAngle)
helpAngle = 0


spd1 = 100
angle2 = 0
angle1 = 0


while time.time() - start_time < game_time:
    update_frame.wait()
    update_frame.clear()

    spd1 = int(abs(angle2) / 1.8 /2)

    


    pos1 = posCheck(3)[0]
    if posCheck(3)[1]:
        angle1 = posCheck(2)[1]
    if helpAngle == 0:
        helpAngle = angle1

    # if angle1 is not None:
    #     print(math.degrees(angle1))

    spd1 = NormalizeSpeed(spd1)

    angle2 = math.degrees(angle1 - goalAngleRads + helpAngle)
    angle2= normalize_angle(angle2)
    print(angle2)

    dir1 = TurnDirCheck(angle2)


    if abs(angle2) < 10:
        SendIt(0,0)
        print("found it")
        break
    else:
        Turn(spd1, dir1)

    time.sleep(0.1)



print("!!!!!")
sock.sendto(bytes("0;0", "utf-8"), (portIp, gobPort))
sock.close()
