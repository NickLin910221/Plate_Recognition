import io
import socket
import pickle
import argparse
import cv2
import numpy as np
import torch
from plate import Plate
from PIL import Image
import os
import loguru
import time
import yaml

loguru.logger.add(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./logs/video2plate.log"), rotation="500MB", encoding="utf-8", enqueue=True, retention="28 days")

abs_path = os.path.dirname(os.path.abspath(__file__)) + "/"
model_plate = torch.hub.load(abs_path + 'yolov5_plate_v5m', 'custom', path = abs_path + 'yolov5_plate_v5m/runs/train/exp/weights/best.pt', source='local')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_plate.to(device)

cnt = 0

def through(img, force):
    global cnt
    stream = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"config.yaml"), 'r')
    data = yaml.load(stream, Loader=yaml.FullLoader)
    start_time = time.time()
    res = model_plate(img)
    cv2.imwrite(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./images/{time.time()}.jpg"), img)
    end_time = time.time()
    if cnt == 100 or force:
        data['configs']['video2plate_response_time'] = end_time - start_time
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"config.yaml"), 'w') as yaml_file:
            yaml_file.write( yaml.dump(data, default_flow_style=False))
        cnt = 0
    cnt += 1
    return res

def plate_detect(socket, obj):
    # Convert the byte stream to an image and save it
    # loguru.logger.info(f"image")
    byte_stream = io.BytesIO(obj.img)
    image = Image.open(byte_stream)
    # image.save(OUTPUT_IMAGE_PATH)
    cv_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    results = through(cv_image, False)
    # Results
    coordinate = results.xyxy[0]
    for plate in coordinate:
        loguru.logger.info(f"Detect {len(coordinate)} plate(s).")
        if int((plate[2] - plate[0]) * (plate[3] - plate[1])) > 2500:
            obj.set_plate(plate[0], plate[1], plate[2], plate[3])
            socket.sendall(len(pickle.dumps(obj)).to_bytes(8, 'big'))
            socket.sendall(pickle.dumps(obj))
        
class Server:
    __slots__ = ["SERVER_IP", "SERVER_PORT", "socket", "_socket_"]
    def __init__(self, ip, port):
        self.SERVER_IP = ip
        self.SERVER_PORT = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.socket.listen(1)
        loguru.logger.info(f"Run video2plate server listen on {ip}:{port}")
        self._socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_.connect(("plate2char", 30301))
        loguru.logger.info(f"Connect to plate2char server on plate2char:30301")
    
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
                    plate_detect(self._socket_, received_obj)
                    
            finally:
                # Clean up the connection
                connection.close()

    def close(self):
        self._socket_.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_character', type=bool, default=False)
    opt = parser.parse_args()
    server = Server("0.0.0.0", 3030)
    server.run()