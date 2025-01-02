import socket
import time
import cv2
import cv2.aruco as aruco
import numpy as np
import math
import threading

capture = cv2.VideoCapture("http://localhost:8080")

ip_address = "127.0.0.1"
robot_port = 3002
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
parameters = aruco.DetectorParameters()

#coordinates and state
myCoords = (0, 0)
hisCoords = (0, 0)
baseCoords = (0, 0)
endCoords = (0, 0)
ids = None
corners = None
frame = None

#event for signaling threads to stop
stop_event = threading.Event()

def send_command(command):
    """Send a command to the robot via UDP."""
    sock.sendto(command.encode(), (ip_address, robot_port))

def stop():
    print("stopping")
    send_command("0;0")

def turn_right():
    print("turning right")
    send_command("100;-100")

def turn_left():
    send_command("-100;100")

def forward():
    send_command("200;200")

def backward():
    print("going backwards")
    send_command("-200;-200")

def turn_right_degrees(deg):
    timer = deg / 360 * 0.5
    send_command("100;-100")
    time.sleep(timer)
    stop()
    time.sleep(0.1)

def forward_mm(mms):
    timer = mms / 400
    send_command("200;200")
    time.sleep(timer)
    stop()
    time.sleep(0.5)

#reads frame and turns it into grayscale
def capture_frame():
    global frame, ids, corners
    while not stop_event.is_set():
        ret, frame = capture.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        time.sleep(0.04)

def process_markers():
    global myCoords, hisCoords, baseCoords, endCoords
    while not stop_event.is_set():
        if ids is not None:
            myCoords = hisCoords = baseCoords = endCoords = (0, 0)
            for i in range(len(ids)):
                marker_id = ids[i][0]
                center = np.mean(corners[i][0], axis=0)
                if marker_id == 2:
                    myCoords = center
                elif marker_id == 3:
                    hisCoords = center
                elif marker_id == 47:
                    baseCoords = center
                elif marker_id == 48:
                    endCoords = center

            myCoords = myCoords * (1500 / 700)
            hisCoords = hisCoords * (1500 / 700)
            dist_x = hisCoords[0] - myCoords[0]
            dist_y = hisCoords[1] - myCoords[1]

            degs_to_turn = math.degrees(math.atan2(dist_y, dist_x))
            if dist_x < 0:
                degs_to_turn += 180
            elif dist_y < 0:
                degs_to_turn += 360

            distance_to_travel = math.hypot(dist_x, dist_y)

            print(f"Turning {degs_to_turn} degrees, moving {distance_to_travel} mm")

            turn_right_degrees(degs_to_turn)
            forward_mm(distance_to_travel)
            stop()

        time.sleep(0.1)

def display_frame():
    global frame
    while not stop_event.is_set():
        if frame is not None:
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break

#start threads
threads = [
    threading.Thread(target=capture_frame, daemon=True),
    threading.Thread(target=process_markers, daemon=True),
    threading.Thread(target=display_frame, daemon=True)
]

for thread in threads:
    thread.start()

#keep the main thread alive
try:
    while not stop_event.is_set():
        time.sleep(1)
except KeyboardInterrupt:
    stop_event.set()

#cleanup
for thread in threads:
    thread.join()

capture.release()
cv2.destroyAllWindows()
sock.close()
