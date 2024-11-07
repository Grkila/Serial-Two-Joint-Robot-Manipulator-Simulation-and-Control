import copy
import argparse
import socket
import time
import cv2 as cv
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=620)#960
    parser.add_argument("--height", help='cap height', type=int, default=480)#540

    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence", help='min_detection_confidence', type=float, default=0.6)
    parser.add_argument("--min_tracking_confidence", help='min_tracking_confidence', type=int, default=0.4)

    args = parser.parse_args()

    return args

def main():
    global mode, root, btn_drawing, btn_hand_recognition
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    use_static_image_mode = args.use_static_image_mode
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence

    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=use_static_image_mode,
        max_num_hands=1,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    UDP_IP = "localhost"
    UDP_PORT = 1122
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)

    mode = 'hand_tracking'
    root = tk.Tk()
    root.title("Mode Selection")
    root.geometry("300x150")

    btn_drawing = ttk.Button(root, text="Drawing Mode", command=lambda: switch_mode('drawing', cap, hands, sock, UDP_IP, UDP_PORT), width=20)
    btn_drawing.pack(pady=20)

    btn_hand_recognition = ttk.Button(root, text="Hand Recognition Mode", command=lambda: switch_mode('hand_tracking', cap, hands, sock, UDP_IP, UDP_PORT), width=30)
    btn_hand_recognition.pack(pady=20)

    root.mainloop()

def switch_mode(new_mode, cap, hands, sock, UDP_IP, UDP_PORT):
    global mode, root, btn_drawing, btn_hand_recognition
    mode = new_mode
    cv.destroyAllWindows()
    if mode == 'drawing':
        drawing_mode(sock, UDP_IP, UDP_PORT)
    else:
        hand_recognition_mode(cap, hands, sock, UDP_IP, UDP_PORT)

def drawing_mode(sock, UDP_IP, UDP_PORT):
    global canvas, num_of_drawing_points, last_points

    def draw_send_button():
        cv.rectangle(canvas, (550, 420), (630, 470), (0, 255, 0), -1)
        cv.putText(canvas, 'Send', (560, 455), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def send_points(array, time_wait):
        for point in array:
            normalized_x, normalized_y = (point[0] / 640) * 2 - 1, -((point[1] / 480) * 2 - 1)
            normalized_x = round(normalized_x, 1)
            normalized_y = round(normalized_y, 1)
            try:
                payload = '[' + str(normalized_x) + ',' + str(normalized_y) + ']'
                sock.sendto(payload.encode('utf-8'), (UDP_IP, UDP_PORT))
                print(f"{payload}")
                time.sleep(time_wait)
            except BlockingIOError:
                pass

    def click_event(event, x, y, flags, param):
        global canvas, last_points

        if 550 <= x <= 630 and 420 <= y <= 470 and event == cv.EVENT_LBUTTONDOWN:
            send_points(last_points, 2)
        elif event == cv.EVENT_LBUTTONDOWN:
            last_points.append((x, y))
            last_points = last_points[-num_of_drawing_points:]

    def draw_grid(canvas, spacing):
        height, width = canvas.shape[:2]

        for i in range(0, height, spacing):
            cv.line(canvas, (0, i), (width, i), (200, 200, 200), 1)

        for j in range(0, width, spacing):
            cv.line(canvas, (j, 0), (j, height), (200, 200, 200), 1)

        center_y = height // 2
        cv.line(canvas, (0, center_y), (width, center_y), (0, 0, 0), 1)

        center_x = width // 2
        cv.line(canvas, (center_x, 0), (center_x, height), (0, 0, 0), 1)

        cv.putText(canvas, '-1.5', (10, center_y + 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv.putText(canvas, '1.5', (width - 20, center_y + 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        cv.putText(canvas, '1', (center_x + 10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv.putText(canvas, '-1', (center_x + 10, height - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    cv.namedWindow('Canvas')
    cv.setMouseCallback('Canvas', click_event)
    num_of_drawing_points = 5
    last_points = []

    while True:
        canvas = 255 * np.ones(shape=[480, 640, 3], dtype=np.uint8)
        draw_grid(canvas, 20)
        cv.putText(canvas, 'Press "e" to escape', (140, 15), cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(canvas, '"i" -> ++', (10, 35), cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(canvas, '"k" -> --', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv.LINE_AA)
        draw_send_button()
        for i, point in enumerate(last_points):
            cv.circle(canvas, point, 5, (0, 255, 0), -1)
            if i > 0:
                cv.line(canvas, last_points[i-1], point, (255, 0, 0), 2)
        font = cv.FONT_HERSHEY_SIMPLEX
        cv.putText(canvas, f'Points: {num_of_drawing_points}', (10, 20), font, 0.5, (0, 0, 0), 1, cv.LINE_AA)

        cv.imshow('Canvas', canvas)
        key_pressed = cv.waitKey(1) 

        if key_pressed == ord('e'):
            break
        elif key_pressed == ord('i'):
            num_of_drawing_points += 1
        elif key_pressed == ord('k') and num_of_drawing_points > 1:
            num_of_drawing_points -= 1

        last_points = last_points[-num_of_drawing_points:] 

    cv.destroyAllWindows()

def hand_recognition_mode(cap, hands, sock, UDP_IP, UDP_PORT):
    
    def draw_axes(image, width, height):
        cv.line(image, (0, height // 2), (width, height // 2), (0, 0, 0), 1)
        cv.line(image, (width // 2, 0), (width // 2, height), (0, 0, 0), 1)
        return image

    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    
    while True:

        key = cv.waitKey(1) 
        if key == ord('e'):  
            break

        ret, image = cap.read()
        if not ret:
            break
        image = cv.flip(image, 1)  
        debug_image = copy.deepcopy(image)
        debug_image = draw_axes(debug_image, image.shape[1], image.shape[0]) 
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        if results.multi_hand_landmarks is not None:
            for hand_landmarks in results.multi_hand_landmarks:
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                pre_processed_landmark_list = pre_process_landmark(landmark_list, 960, 540)

                print(pre_processed_landmark_list)
                MESSAGE = str(pre_processed_landmark_list).encode('utf-8')
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

                debug_image = draw_landmarks(debug_image, landmark_list)

        debug_image = draw_info(debug_image)

        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point

def pre_process_landmark(landmark_list, image_width, image_height):
    base_x, base_y = image_width // 2, image_height // 2

    point_8 = landmark_list[8]
    relative_x = point_8[0] - 310
    relative_y = -(point_8[1] - 240)

    normalized_x = relative_x / 310
    normalized_y = relative_y / 240

    normalized_x = normalized_x / 0.7
    normalized_y = normalized_y / 0.7

    normalized_x = max(-1, min(normalized_x, 1))
    normalized_y = max(-1, min(normalized_y, 1))

    normalized_x = round(normalized_x, 1)
    normalized_y = round(normalized_y, 1)

    normalized_point_8 = [normalized_x, normalized_y]

    return normalized_point_8

def draw_landmarks(image, landmark_point):
    if len(landmark_point) > 0:
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]), (255, 255, 255), 2)

        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]), (255, 255, 255), 2)

        cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]), (255, 255, 255), 2)

        cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]), (255, 255, 255), 2)

        cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]), (255, 255, 255), 2)

        cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]), (255, 255, 255), 2)
        cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[17]), (0, 0, 0), 6)
        cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[17]), (255, 255, 255), 2)

    for i, point in enumerate(landmark_point):
        if i == 8:
            cv.circle(image, tuple(point), 7, (0, 255, 0), -1)
        else:
            cv.circle(image, tuple(point), 5, (255, 255, 255), -1)
            cv.circle(image, tuple(point), 5, (0, 0, 0), 1)

    return image

def draw_info(image):
    
    cv.putText(image, 'Press "e" to escape', (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv.LINE_AA)
    cv.putText(image, 'Press "e" to escape', (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

    return image


if __name__ == '__main__':
    main()
