import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math
import random
import threading

game_time = 160
#portit, jotka kuuntelevat UDP-viestejä:
gobIp = "192.168.1.107"
gobPort = 3000
frndIp = "192.168.1.108"
frndPort = 3000

#initoidaan aruco-kirjasto
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
#initoidaan sock joka lähettää UDP-viestit
sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)

#miltä hsv-rangelta robotti tunnistaa pallojen värit
# lower_magenta = np.array([140, 100, 100])
# upper_magenta = np.array([160, 255, 255])
# lower_green = np.array([50, 100, 100])
# upper_green = np.array([70, 255, 255])
# vaihtaa tunnistettavien pallojen värin keltaiseksi ja punaiseksi
lower_magenta = np.array([170, 150, 150])
upper_magenta = np.array([180, 255, 255])
# lower_green = np.array([28, 150, 200])
# upper_green = np.array([32, 255, 255])

lower_green = np.array([25, 100, 150])  # More yellowish and less saturated/bright
upper_green = np.array([40, 255, 255])


capName =(0) #tän voi vaihtaa jos kuvafiidi tulee eri paikasta
#capName =(0, cv2.CAP_DSHOW)

#aruco idt:
ownGoalId = 46
enemyGoalId = 49
goblinID= 25
friendID = 24



pointA = (203, 318)  #Keskilinja pitää varmaan hardkoodata, jos ei haluu muuttaa logiikkaa paljoa
pointB = (356, 182)
pointA1 = (491, 400)
pointB1 = (300, 454)
pointA2 = (190, 25)
pointB2 = (33, 170)

pointOwnGoal = (396, 427) #nää on maalintekoalueiden keskipiste
pointEnemyGoal = (112, 98)

middlePoint = (350, 258)



ownGoal = (492, 453)

frndPointA =(70, 370)
frndPointB = (396, 70) #pitää vaihtaa, random pojot joihin frnd palaa cp 0:ssa

lowerX = 33
upperY = 491
upperX = 454
lowerY = 25 #voi tarkistaa ja tweakata riippuen areenasta

#IDitä ja pojoja simulaattorissa:
# 2 on goblin
# 3 friend
# 47 on 00
# 48 on 1500/1500
#50 on oma maali
#49 on vihun maali
#0 on nuolinäppäinvihiu
#1 on wasdvihu


ret = ids = rejectedImgPoints = corners = contours_green = contours_magenta = magenta_centers = green_centers = None
lock_the_frame = threading.Lock()
update_frame = threading.Event()


def CapFrame(): #funktio joka käsittelee kuvafiidiä
    global ret, ids, rejectedImgPoints, corners, contours_green, contours_magenta, magenta_centers, green_centers
    global capture
    while True:
        capture = cv2.VideoCapture(capName, cv2.CAP_DSHOW)
        #capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)

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
        time.sleep(0.001)



def get_contour_centers(contours): #tätä tarvitaan palloihin
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centers.append((cX, cY))
    return centers


def posCheck(id): #tunnistaa missä aruco marker on ja mikä sen kulma on
    global corners, ids
    coords = None
    angle = None
    with lock_the_frame:
        if ids is not None and corners is not None:
            for i in range(len(ids)):
                if ids[i][0] == id:
                    coords = (corners[i][0][:, 0].mean(), corners[i][0][:, 1].mean())
                    corner = corners[i][0]
                    vector = corner[3] - corner[2] #joskus kamerasta liittyen pitää käyttää eri kulmia, jos robotti kääntyy 180 pieleen, koita vaihtaa päittäin 2-3 -> 3-2
                    angle = math.atan2(vector[1], vector[0])
                    break
    return coords, angle

def SendIt(lv, rv): #leftvalue, rightvalue lähettää viestin
    lv = -lv
    rv = -rv
    if abs(rv) > 32:
        rv = rv * 0.65
    rv = int(rv)
    command = f"{lv};{rv}"
    sock.sendto(command.encode(), (gobIp, gobPort))
    #print ("gob" + command)
    time.sleep(0.1)

def SendItFriend(lv, rv): #leftvalue, rightvalue
    lv = -lv
    rv = -rv
    if abs(lv) > 32:
        lv = lv * 0.65
    lv = int(lv)
    command = f"{lv};{rv}"
    sock.sendto(command.encode(), (frndIp, frndPort))
    #print ("frnd" + command)
    time.sleep(0.1)

def pointingAngle(coords, angle, targetCoords): #katsoo mikä on robotin ja targetin kulman erotus
    vector = np.array(targetCoords) - np.array(coords)
    vectorAngle = np.arctan2(vector[1], vector[0])
    vectorAngle += np.pi / 2
    angleDiff = (angle - vectorAngle)
    angleDiff = ((angleDiff + np.pi) % (2 * np.pi) - np.pi)
    return np.degrees(angleDiff)

def Turn(speed, dir =str): #dir ccw, tai cw, clockwise, counterclock, kääntää robottia suuntaan dir nopeudella speed
    if dir == "cw":
        SendIt(-speed, speed)
        #print(dir)
    elif dir == "ccw":
        SendIt(speed,-speed)
        #print(dir)
    else:
        SendIt (0,0)
        #print("anna toinen")

def TurnFriend(speed, dir =str): #sama kuin ylempi, mutta toiselle robotille
    if dir == "cw":
        SendItFriend(-speed, speed)
    elif dir == "ccw":
        SendItFriend(speed,-speed)
    else:
        SendItFriend (0,0)
        print("anna toinen")

def dot_product(v1, v2): #pistetulo, apufunktio, geometriassa hyödyllinen
    return v1[0] * v2[0] + v1[1] * v2[1]

def IsItInside(target, a, b, c, d): #tarkistaa onko target nelikulmion sisällä, a...c on kulmat
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

def IsItLeft(A, B, P): #tarkistaa onko piste P, A:n ja B:n välisen viivan vasemmalla puolella
    #syötä a ja b eri järjestyksessä tai käytä negaatiota niin saat onko piste oikealla

    A = np.array(A)
    B = np.array(B)
    P = np.array(P)

    # Vector from A to B
    AB = B - A

    # Vector from A to P
    AP = P - A

    # Calculate the cross product
    cross_product = AB[0] * AP[1] - AB[1] * AP[0]

    # If cross product is positive, P is to the left of vector AB
    return cross_product > 0

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

def Distance(point1, point2): #euklidinen etäisyys 2 pisteen välillä pikseleissä
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


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

#testikäytössä, ei toimi fyys robolla
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
def CoordsToMms(coords):
    return coords / 700 * 1500
def WhereTo(coords, angle, target):
    angle1 = pointingAngle(coords, angle, target)
    dist1 = CoordsToMms(Distance(coords, target))
    return angle1, dist1


frcheckpoint = 0

FriendGoLeft = True


friendCoords = (0,0)
frangle2 = 0.0
tempDeg = 0.0
tempDis = 0.0
frSpd1 = 0
frMoveSpd1 = 100
frGoLeft = True
frdir1 = ""


frHelpDist = 2000
frHelpDist2 = 2000
frTar1 = (0,0)



frtar0 =(0,0)

#x:n ja y:n arvot kentän reunoissa, pitää vaihtaa riippuen areenasta
# lowerX = 85
# upperY = 70
# upperX = 460
# lowerY = 440 #voi tarkistaa ja tweakata riippuen areenasta

# lowerX = 440
# upperY = 85
# upperX = 70
# lowerY = 460 #voi tarkistaa ja tweakata riippuen areenasta

# lowerX = 460
# upperY = 440
# upperX = 85
# lowerY = 70 #voi tarkistaa ja tweakata riippuen areenasta



def NormalizeTarget(point = tuple):#jos piste on kentän ulkopuolella, laittaa sen takas
    x = point[0]
    y = point[1]
    if x < lowerX:
        x = lowerX
        print("normalizing... beep beep")
    if x > upperX:
        x = upperX
        print("normalizing... beep beep")
    if y < lowerY:
        y = lowerY
        print("normalizing... beep beep")
    if y > upperY:
        y = upperY
        print("normalizing... beep beep")
    point = (x, y)
    return point

def FriendIt(): #tämä funktio ohjaa friend-robottia
    while True:
        global frangle2, frGoLeft, frHelpDist, frHelpDist2, frdir1, frtar0, frcheckpoint, frspd1, tarBall1, frmoveSpeed, frtar1
        global frndPointA, frndPointB
        update_frame.wait()
        update_frame.clear()
        frpos1 = posCheck(friendID)[0]
        frangle1 = posCheck(friendID)[1]

        frspd1 = int(abs(frangle2) / 1.8 * 0.5)



        frmyCoords, frmyAngle = posCheck(friendID)
        if frmyCoords is None or frmyAngle is None:
            continue

        #frspd1 = int(abs(frangle2) / 1.8 * 1)
        frspd1 = NormalizeSpeed(frspd1)
        frdir1 = TurnDirCheck(frangle2)


        with lock_the_frame:
            comparingCenters = green_centers
            comparingCentersLeft = [center for center in comparingCenters if IsItLeft(pointA1, pointA2, center)]
            comparingCentersRight = [center for center in comparingCenters if not IsItLeft(pointB1, pointB2, center)]
            if frGoLeft: 
                worseGreenCenters = [center for center in green_centers if IsItLeft(pointA1, pointA2, center)]
            else:
                worseGreenCenters = [center for center in green_centers if not IsItLeft(pointB1, pointB2, center)]

        if frcheckpoint == 0:
            
            if frGoLeft:
                #print ("seeking frpA")
                frtar0 = frndPointA
            else:
                #print ("seeking frpB")
                frtar0 = frndPointB
            frtar0 = NormalizeTarget(frtar0)
            frangle2 = pointingAngle(frpos1, frangle1, frtar0)
            if abs(frangle2) < 10:
                frcheckpoint +=1
            else:
                TurnFriend(frspd1, frdir1)
        if frcheckpoint == 1:
            #print("going to point")
            frmoveSpeed = Distance(frpos1, frtar0) / 2
            frmoveSpeed = NormalizeSpeed(frmoveSpeed)
            SendItFriend(frmoveSpeed, frmoveSpeed)

            if frHelpDist2 < Distance(frpos1, frtar0): # jos  mentiin ohi lähetetään stop
                frcheckpoint +=1
                SendItFriend(0,0)
                #print("at point")
            else:
                SendItFriend(frmoveSpeed, frmoveSpeed)

            frHelpDist2 = Distance(frpos1, frtar0)

        if frcheckpoint == 2:
            ("seeking balls")
            if worseGreenCenters:
                tarBall1 = min(worseGreenCenters, key=lambda center: Distance(center, ownGoal))
                frcheckpoint += 1
            else:
                frcheckpoint = 0

                frtar0 = (0,0)
                frspd1 = 100
                frangle2 = 0
                tarBall1 = (0,0)
                frmoveSpeed = 100
                frHelpDist = 2000
                frdir1 = "cw"
                
                frtar1 =(0,0)
                if frGoLeft == True:
                    if not comparingCentersLeft:
                        frGoLeft = False
                else:
                    if not comparingCentersRight:
                        frGoLeft = True

        if frcheckpoint == 3:
            #print ("ball found, calc billman")
            frtar1 = BilliardManeuver(frpos1, ownGoal, tarBall1)[0]
            if Distance(frtar1, ownGoal) < Distance(tarBall1, ownGoal):
                if frGoLeft == True:
                    frtar1 = BilliardManeuver(pointA2, tarBall1, ownGoal)[0] #ei ohjaa roboa maalin ja pallon väliin
                else:
                    frtar1 = BilliardManeuver(pointB2, tarBall1, ownGoal)[0]
            frtar1 = NormalizeTarget(frtar1)
            frcheckpoint += 1

        if frcheckpoint == 4:
            #print("turning")
            frangle2 = pointingAngle(frpos1, frangle1, frtar1)
            if abs(frangle2) < 10:
                frcheckpoint +=1
            else:
                TurnFriend(frspd1, frdir1)

        if frcheckpoint == 5:
            #print ("going to bill man")
            frmoveSpeed = Distance(frpos1, frtar1) / 5
            frmoveSpeed = NormalizeSpeed(frmoveSpeed)
            SendItFriend(frmoveSpeed, frmoveSpeed)

            if frHelpDist < Distance(frpos1, frtar1): # jos  mentiin ohi lähetetään stop
                frcheckpoint +=1
                SendItFriend(0,0)        

            else:
                SendItFriend(frmoveSpeed, frmoveSpeed)

            frHelpDist = Distance(frpos1, frtar1)

        if frcheckpoint == 6:
            #print ("turning to goal")
            #frtar3 = ownGoal
            frangle2 = pointingAngle(frpos1, frangle1, ownGoal)
            if abs(frangle2) < 10:
                frcheckpoint +=1
            else:
                TurnFriend(frspd1, frdir1)

        if frcheckpoint == 7:
            #print("going to goal")
            SendItFriend(100,100)
            time.sleep(4)
            frcheckpoint = 0

            frtar0 = (0,0)
            frspd1 = 100
            frangle2 = 0
            tarBall1 = (0,0)
            frmoveSpeed = 100
            frHelpDist = 2000
            frHelpDist2 = 2000
            frdir1 = "cw"
            
            frtar1 =(0,0)
            if frGoLeft == True:
                if not comparingCentersLeft:
                    frGoLeft = False
            else:
                if not comparingCentersRight:
                    frGoLeft = True


        time.sleep(0.01)

pixTol = 25 #pixel tolerance for stuckcheker


def StuckChecker(): #jos friend on 10 sekkaa samassa pisteessä, peruuttaa vähän ja palauttaa checkpoint 0:n
    global goblinID, friendID, checkpoint, frcheckpoint
    global frangle2, frGoLeft, frHelpDist, frHelpDist2, frdir1, frtar0, frcheckpoint, frspd1, tarBall1, frmoveSpeed, frtar1
    update_frame.wait()
    update_frame.clear()

    temp1 = (0,0)
    temp2 = (1000, 1000)
    temp1f = (0,0)
    temp2f=(1000,1000)
    while True:
        temp1 = posCheck(goblinID)[0]
        if Distance(temp1, temp2) < pixTol:
            #print("gob stuck?") #en tiiä onko tarpeen, gob jää harvoin jumiin
            # SendIt(-100,-70)
            # time.sleep(3)
            # SendIt(0,0)
            # checkpoint =(0)
            #tänne var nollaus?

            temp2 = posCheck(goblinID)[0]
            temp1f = posCheck(friendID)[0]
        if Distance(temp1f, temp2f) < pixTol:
            #print("friend stuck")
            SendItFriend(-100,-70)
            time.sleep(1)


            SendItFriend(0,0)

            frcheckpoint =0
            #tänne var nollaus?
            frtar0 = (0,0)
            frspd1 = 100
            frangle2 = 0
            tarBall1 = (0,0)
            frmoveSpeed = 100
            frHelpDist = 2000
            frHelpDist2 = 2000
            frdir1 = "cw"
            
            frtar1 =(0,0)
            

        temp2f = posCheck(friendID)[0]

        #print("meep meep")
        time.sleep(10)




#aloitetaan threadit, capframe, friendit ja stuckchecker
#threadit loppuu, kun main funktio loppuu
frame_capture_thread = threading.Thread(target=CapFrame, daemon=True)
frame_capture_thread.start()

stuckThread = threading.Thread(target= StuckChecker, daemon= True)
stuckThread.start() #pistin tän ennen frndthreadia toivoen, että kuuntelee friendin udp:tä

friendThread = threading.Thread(target= FriendIt, daemon= True)
friendThread.start()
angle2 = 0
start_time = time.time()

spd1 = 100

tar1 = (0, 0)
tar2 = (0,0 )
tar3 = (0,0)

checkpoint = 0
# 0 käänny keskipisteeseen, 1 liiku keskipisteeseen, 2 käänny biljardin tapaan, etc
# joka stepissä lisätään 1 ja vikassa nollataan

moveSpeed = 100
helpDist = 2000
helpDist2 = 2000
goalPos2 = (0,0)
dir1 = "cw"


while time.time() - start_time < game_time: #"main" funktio, ohjaa goblinia
    update_frame.wait()
    update_frame.clear()
    spd1 = int(abs(angle2) / 1.8 * 0.5)


    pos1 = posCheck(goblinID)[0]
    angle1 = posCheck(goblinID)[1]
    

    myCoords, myAngle = posCheck(goblinID)
    if myCoords is None or myAngle is None:
        continue

    with lock_the_frame:
        betterGreenCenters = [center for center in green_centers if IsItInside(center, pointA, pointA1, pointB1, pointB)]
        betterMagentaCenters = [center for center in magenta_centers if IsItInside(center, pointA, pointA2, pointB2, pointB)]
        all_centers = betterGreenCenters + betterMagentaCenters


    spd1 = NormalizeSpeed(spd1)
    dir1 = TurnDirCheck(angle2)
    if checkpoint == 0:
        #print("looking for middle point")
        tar1 = middlePoint
        angle2 = pointingAngle(pos1, angle1, tar1)
        if abs(angle2) < 5:
            checkpoint +=1
        else:
            Turn(spd1, dir1)



    if checkpoint == 1:
        moveSpeed = Distance(pos1, tar1) / 5
        #print ("going to center")
        moveSpeed = NormalizeSpeed(moveSpeed)
        SendIt(moveSpeed, moveSpeed)

        if helpDist < Distance(pos1, tar1): # jos  mentiin ohi lähetetään stop
            checkpoint +=1
            SendIt(0,0)        

        else:
            SendIt(moveSpeed, moveSpeed)

        helpDist = Distance(pos1, tar1)
    
    if checkpoint == 2:
        if all_centers:
            #jos on palloja alueella, valitaan 1, jos ei, palataan checkpoint 0:n
            targetBall = random.choice(all_centers)
            if targetBall in green_centers:
                goalPos2 = posCheck(ownGoalId)[0]
            elif targetBall in magenta_centers:
                goalPos2 = posCheck(enemyGoalId)[0]
            tar2 = BilliardManeuver(pos1, targetBall, goalPos2)[0]
            checkpoint += 1
        else:
            checkpoint = 0
            #nollataan kaikki muuttujat kun palataan cp 0:n
            angle2 = 0
            spd1 = 100
            tar1 = (0, 0)
            tar2 = (0,0 )
            tar3 = (0,0)
            moveSpeed = 100
            helpDist = 2000
            helpDist2 = 2000
            goalPos2 = (0,0)
    
    if checkpoint == 3:
        #print ("found ball, seeking")
        angle2 = pointingAngle(pos1, angle1, tar2)
        if abs(angle2) < 5:
            checkpoint +=1
            SendIt(0,0)
        else:
            Turn(spd1, dir1)

    if checkpoint == 4:
        #print ("going to bill man")
        moveSpeed = Distance(pos1, tar2) / 5
        moveSpeed = NormalizeSpeed(moveSpeed)
        SendIt(moveSpeed, moveSpeed)

        if helpDist2 < Distance(pos1, tar2):
            checkpoint +=1
            SendIt(0,0)        

        else:
            SendIt(moveSpeed, moveSpeed)

        helpDist2 = Distance(pos1, tar2)
    
    if checkpoint == 5:
        tar3 = goalPos2
    if checkpoint == 5:
        #print("turning to goal")
        angle2 = pointingAngle(pos1, angle1, tar3)
        if abs(angle2) < 5:
            checkpoint +=1
        else:
            Turn(spd1, dir1)
    if checkpoint == 6:
        #print("going to goal")
        SendIt(100,100)
        time.sleep(3) #täs on taas time sleeppi ei varmaan haittaa, mut vois tietty muuttaa
        checkpoint = 0

        #nollataan kaikki muuttujat kun palataan cp 0:n
        angle2 = 0
        spd1 = 100
        tar1 = (0, 0)
        tar2 = (0,0 )
        tar3 = (0,0)
        moveSpeed = 100
        helpDist = 2000
        helpDist2 = 2000
        goalPos2 = (0,0)
        
    


    time.sleep(0.01)


#Lähetetään vielä varmuuden vuoksi viestit roboteille, että pysähtyisivät
print("!!!!!")
sock.sendto(bytes("0;0", "utf-8"), (gobIp, gobPort))
sock.sendto(bytes("0;0", "utf-8"), (frndIp, frndPort))
sock.close()



capture.release()