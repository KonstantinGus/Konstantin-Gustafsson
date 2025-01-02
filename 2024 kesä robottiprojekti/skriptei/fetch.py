import socket
import time
import cv2
import numpy as np

#Trying to get the robot to go to the nearest green ball

#functions that control the robot
def stop(ip, port):
    print("stopping")
    sock.sendto(bytes("0;0", "utf-8"), (ip, port))

def turn_right(ip, port):
    print("turning right")
    sock.sendto(bytes("50;-50", "utf-8"), (ip, port))

def turn_left(ip, port):
    print("turning left")
    sock.sendto(bytes("-50;50", "utf-8"), (ip, port))

def forward(ip, port):
    print("going forward")
    sock.sendto(bytes("100;100", "utf-8"), (ip, port))

def backward(ip, port) :
    print("going backwards")
    sock.sendto(bytes("-100;-100", "utf-8"), (ip, port))

#calculates the distance between green balls and the center of the frame
def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

ip_address = "127.0.0.1"
robot_port = 3001


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

capture = cv2.VideoCapture("http://localhost:8080")

while True:
    #reads a frame from the video feed
    ret, frame = capture.read()
    if not ret:
        break

    #converts the frame from RGB to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #define color green
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([70, 255, 255])

    mask = cv2.inRange(hsv_frame, lower_green, upper_green)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    #find green objects in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

   #find closest ball
    closest_ball_distance = float('inf')
    closest_ball_center = None

    for contour in contours:
        (x, y), _ = cv2.minEnclosingCircle(contour)
        ball_center_x, ball_center_y = int(x), int(y)
        ball_distance = calculate_distance(frame.shape[1] // 2, frame.shape[0] // 2, ball_center_x, ball_center_y)

        if ball_distance < closest_ball_distance:
            closest_ball_distance = ball_distance
            closest_ball_center = (ball_center_x, ball_center_y)

    #go to ball
    if closest_ball_center is not None:
        ball_center_x, ball_center_y = closest_ball_center

        frame_center_x = frame.shape[1] // 2
        if ball_center_x < frame_center_x - 50:
            print("Ball is to the left")
            turn_left(ip_address, robot_port)
        elif ball_center_x > frame_center_x + 50:
            print("Ball is to the right")
            turn_right(ip_address, robot_port)
        else:
            print("Ball is centered")
            forward(ip_address, robot_port)
    else:
        #stop if no ball
        print("No ball detected")
        stop(ip_address, robot_port)

    cv2.imshow("Frame", frame)

    #exit with q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#stop
stop(ip_address, robot_port)
capture.release()
cv2.destroyAllWindows()
sock.close()