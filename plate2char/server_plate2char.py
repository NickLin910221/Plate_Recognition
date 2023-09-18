import io
import socket
import pickle
import argparse
import cv2
import numpy as np
import torch
from plate import Plate
from PIL import Image
import time
import sha256
import datetime
from datetime import timezone, timedelta
import os
import mysql.connector
import loguru
import yaml

loguru.logger.add(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./logs/plate2char.log"), rotation="500MB", encoding="utf-8", enqueue=True, retention="28 days")
abs_path = os.path.dirname(os.path.abspath(__file__)) + "/"
model_char = torch.hub.load(abs_path + 'yolov7', 'custom', path_or_model = abs_path + 'yolov7/best.pt', source='local')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_char.to(device)
cnt = 0

def through(img, force):
    global cnt
    stream = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"config.yaml"), 'r')
    data = yaml.load(stream, Loader=yaml.FullLoader)
    start_time = time.time()
    res = model_char(img)
    end_time = time.time()
    if cnt == 100 or force:
        data['configs']['plate2char_response_time'] = end_time - start_time
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"config.yaml"), 'w') as yaml_file:
            yaml_file.write( yaml.dump(data, default_flow_style=False))
        cnt = 0
    cnt += 1
    return res

def detect_color(img):
    mask_red = cv2.inRange(img, np.array([150, 50, 50]), 
                           np.array([255, 150, 150]))
    red = cv2.bitwise_and(img, img, mask=mask_red)
    mask_white = cv2.inRange(img, np.array([175, 175, 175]), 
                             np.array([255, 255, 255]))
    white = cv2.bitwise_and(img, img, mask=mask_white)
    mask_green = cv2.inRange(img, np.array([0, 25, 0]), 
                             np.array([100, 50, 100]))
    green = cv2.bitwise_and(img, img, mask=mask_green)
    mask_black = cv2.inRange(img, np.array([0, 0, 0]), 
                             np.array([50, 50, 50]))
    black = cv2.bitwise_and(img, img, mask=mask_black)
    mask_yellow = cv2.inRange(img, np.array([150, 100, 0]), 
                              np.array([225, 175, 50]))
    yellow = cv2.bitwise_and(img, img, mask=mask_yellow)
    color_selector = [{"color" : "Red", "number" : cv2.countNonZero(cv2.cvtColor(red, cv2.COLOR_RGB2GRAY))}, 
                      {"color" : "White", "number" : cv2.countNonZero(cv2.cvtColor(white, cv2.COLOR_RGB2GRAY))}, 
                      {"color" : "Green", "number" : cv2.countNonZero(cv2.cvtColor(green, cv2.COLOR_RGB2GRAY))}, 
                      {"color" : "Black", "number" : cv2.countNonZero(cv2.cvtColor(black, cv2.COLOR_RGB2GRAY))}, 
                      {"color" : "Yellow", "number" : cv2.countNonZero(cv2.cvtColor(yellow, cv2.COLOR_RGB2GRAY))}]
    # print(color_selector)
    color_selector.sort(key=lambda x: x["number"], reverse = True)
    return color_selector[0]["color"][0] + color_selector[1]["color"][0]


def decode(code):
    code_list = ['0', '1', '2', '3', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    # code_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    return code_list[int(code)]

def iou(obj1, obj2):
    intersection_area = int((min(obj2[2], obj1[2]) - max(obj2[0], obj1[0])) * (min(obj2[3], obj1[3]) - max(obj2[1], obj1[1])))
    area1 = int((obj1[2] - obj1[0]) * (obj1[3] - obj1[1]))
    area2 = int((obj2[2] - obj2[0]) * (obj2[3] - obj2[1]))
    return intersection_area / (area1 + area2 - intersection_area)

def char_detect(obj):
    # Convert the byte stream to an image and save it
    byte_stream = io.BytesIO(obj.img)
    image = Image.open(byte_stream)
    cv_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    width, height, _ = cv_image.shape
    xmin, xmax, ymin, ymax = obj.xmin, obj.xmax, obj.ymin, obj.ymax
    resize_image = cv_image[ymin:ymax, xmin:xmax]
    # resize_image = cv_image
    gray_image = cv2.cvtColor(np.asarray(resize_image), cv2.COLOR_BGR2GRAY)
    gray_image = cv2.resize(gray_image, (640, 640), interpolation=cv2.INTER_AREA)

    results = through(gray_image, False)
    number = ""
    for i in results.xyxy[0]:
        number += decode(i[5])
    if len(results.xyxy[0]) < 4:
        gray_image_reverse = 255 - gray_image
        results = through(gray_image_reverse, False)
    # Results
    coordinate = results.xyxy[0]
    tmp = []
    for char in coordinate:
        if (int((char[3] - char[1]) * (char[2] - char[0])) < 5000):
            continue
        flag = True
        for index, _char_ in enumerate(tmp):
            if (1 > iou(char[:4], _char_[:4]) > 0.8):
                if char[4] > _char_[4]:
                    tmp.remove(tmp[index])
                flag = False
        if flag and char[4] > 0.75:
            tmp.append([int(char[0]), int(char[1]), int(char[2]), int(char[3]), float(char[4]), decode(int(char[5]))])
    tmp.sort(key=lambda row: (row[0]), reverse=False)
    number, color, filename = "", "", ""
    if 7 >= len(tmp) >= 4:
        for x in tmp:
            number += x[5]
        color = detect_color(cv2.cvtColor(np.asarray(resize_image), cv2.COLOR_BGR2RGB))
        # Labeling every characters
        if opt.label_character:
            for x in tmp:
                cv2.putText(cv_image, x[5] + " " + str(x[4])[:3], (x[0], x[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
                cv2.rectangle(cv_image, (x[0], x[1]), (x[2], x[3]), (0, 255, 0), 2)
        obj.write_number(number)
        cv2.rectangle(cv_image, (obj.xmin, obj.ymin), (obj.xmax, obj.ymax), (0, 255, 0), 2)
        cv_image = cv2.putText(cv_image, obj.get_plate_number(), (obj.xmin, obj.ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
        filename = sha256.encoding(f"{obj.get_plate_number()}_{int(time.time())}")[:10]
        loguru.logger.info(number)
        return obj.get_ts(), number, obj.get_entrance(), color, filename, cv_image, coordinate
    return "", "", "", "", "", cv_image, coordinate

class Server:
    __slots__ = ["SERVER_IP", "SERVER_PORT", "socket", "mysql", "last"]
    def __init__(self, ip, port):
        self.SERVER_IP = ip
        self.SERVER_PORT = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.socket.listen(1)
        loguru.logger.info(f"Run plate2char server listen on {ip}:{port}")
        self.mysql = mysql.connector.connect(host="mysql",
                                            user="root",
                                            password="mcnlab")
        self.last = []
    
    def run(self):
        while True:
            connection, client_address = self.socket.accept()
            try:
                # Receive the image data
                while True:
                    packet_size = int.from_bytes(connection.recv(8), 'big')
                    data = bytearray()
                    while packet_size:
                        packet = connection.recv(4096 if packet_size > 4096 else packet_size)
                        if not packet:
                            break
                        packet_size -= len(packet)
                        data.extend(packet)
                    try:
                        received_obj = pickle.loads(data)
                    except Exception as e:
                        continue

                    ts, plate, entrance, color, filename, image, raw_data = char_detect(received_obj)
                    
                    loguru.logger.info(f"{ts}, {plate}, {entrance}, {color}, {filename}")
                    if (ts != "" and plate != "" and entrance != "" and color != "" and filename != ""):
                        if self.add_cache(received_obj, plate, entrance):
                            cv2.imwrite(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./images/{filename}.jpg"), image)
                            self.insert_db(received_obj.get_ts_to_string(), plate, entrance, color, filename)
                            file = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./raw_data.txt"), 'a')
                            file.write(raw_data)
                            file.close()
                    else:
                        continue
                    del received_obj
            finally:
                # Clean up the connection
                connection.close()

    def add_cache(self, obj, plate, entrance):
        for x in self.last:
            loguru.logger.info(f"{x.get_plate_number()}, {x.get_entrance()}")
        if len(self.last) == 0:
            self.last.append(obj)
            return True
        for index, record in enumerate(self.last):
            if record.get_entrance() == entrance:
                if (record.get_ts() <= obj.get_ts() and record.get_plate_number() != plate) or (obj.get_ts() - record.get_ts() > 15 and record.get_plate_number() == plate):
                    del self.last[index]
                    self.last.append(obj)
                    return True
                else: 
                    return False
            else: 
                return False
        self.last.append(obj)
        return True

    def insert_db(self, ts, plate, entrance, color, image):
        cursor = self.mysql.cursor()
        sql = f"insert into db.backend_history (Timestamp, Plate, Entrance, Color, Image) VALUES ('{ts}', '{plate}', '{entrance}', '{color}', '{image}')"
        cursor.execute(sql)
        self.mysql.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_character', type=bool, default=False)
    opt = parser.parse_args()
    through(cv2.imread(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./no_signal.jpg")), True)
    server = Server("0.0.0.0", 30301)
    server.run()