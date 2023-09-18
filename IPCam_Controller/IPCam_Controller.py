import io
import socket
import pickle
import cv2
from PIL import Image
from plate import Plate
import os
from IPCam import IPCam
import mysql.connector
import time
import yaml
import loguru

loguru.logger.add(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./logs/IPCam_Controller.log"), rotation="500MB", encoding="utf-8", enqueue=True, retention="28 days")

class Client:
    __slots__ = ["SERVER_IP", "SERVER_PORT", "socket", "_mysql_", "cache_source", "interval"]
    def __init__(self, ip, port):
        self.SERVER_IP = ip
        self.SERVER_PORT = port
        loguru.logger.info(f"Connect to video2plate server on {ip}:{port}")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.SERVER_IP, self.SERVER_PORT))
        self.cache_source = []
        self._mysql_ = mysql.connector.connect(host="mysql",
                                                user="root",
                                                password="mcnlab")
        cursor = self._mysql_.cursor()
        cursor.execute("SELECT * FROM db.backend_ipcamera")
        result = cursor.fetchall()

        stream = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./config.yaml"), 'r')
        data = yaml.load(stream, Loader=yaml.FullLoader)

        self.interval = float(data['configs']['video2plate_response_time']) * 1.5 + float(data['configs']['plate2char_response_time']) * 1.5
        for x in result:
            loguru.logger.info(f"Monitor on source : {x[0]}, entrance name : {x[2]}")
            self.cache_source.append(IPCam(x[0], x[2], 30))
        for x in self.cache_source:
            x.run()

    def run(self):
        cnt = 0
        while True:
            for x in self.cache_source:
                img, ts, status = x.getimg()
                if status == True:
                    cv2.imwrite(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./1.jpg"), img)
                    self.send(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), x.getentrance_name())
                    time.sleep(self.interval)
                    cnt += 1

    def send(self, img, entrance):
        # Load and convert the image into a byte stream
        byte_stream = io.BytesIO()
        img.save(byte_stream, format='JPEG')
        image_data = byte_stream.getvalue()
        # Send the image data
        data = Plate(image_data, entrance, 0, 0, 0, 0)
        self.socket.sendall(len(pickle.dumps(data)).to_bytes(8, 'big'))
        self.socket.sendall(pickle.dumps(data))
        # Close the socket

    def close(self):
        self.socket.close()
       
        
if __name__ == "__main__":
    client = Client("video2plate", 3030)
    # client.send(Image.fromarray(cv2.cvtColor(cv2.imread(os.path.join(os.path.abspath(os.path.dirname(__file__)), "AQM6955.jpg")), cv2.COLOR_BGR2RGB)), "test")
    # client.send(Image.fromarray(cv2.cvtColor(cv2.imread(os.path.join(os.path.abspath(os.path.dirname(__file__)), "5799KE.jpeg")), cv2.COLOR_BGR2RGB)), "test")
    # cv2.imwrite(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./{time.time()}.jpg"), cv2.cvtColor(cv2.imread(os.path.join(os.path.abspath(os.path.dirname(__file__)), "5799KE.jpeg")), cv2.COLOR_BGR2RGB))
    client.run()
    # cap = cv2.VideoCapture(os.path.join(os.path.abspath(os.path.dirname(__file__)), "video13.mp4"))
    # sampling = 3
    # cnt = 0
    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     if ret == False:
    #         continue
    #     else:
    #         if cnt % sampling == 0:
    #             # try:
    #                 print(cnt)
    #                 cv2.imwrite(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./{time.time()}.jpg"), frame)
    #                 client.send(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), "test")
    #                 time.sleep(client.interval)
    #             # except BrokenPipeError as e:
    #             #     continue

    #     cnt += 1
    # cap.release()
    client.close()