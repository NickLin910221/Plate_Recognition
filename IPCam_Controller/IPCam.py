import cv2
import threading
import os
import time
from threading import Lock

class IPCam:
    __slots__ = ["img", "status", "url", "entrance_name", "source", "flag", "nosignal", "fps", "last_frame", "lock"]

    def __init__(self, url, entrance_name, fps, flag = True) -> None:
        self.url = url
        self.entrance_name = entrance_name
        self.status = False
        self.last_frame = time.time()
        self.fps = fps
        self.img = None
        self.lock = Lock()
        self.source = cv2.VideoCapture(self.url)
        self.nosignal = cv2.imread(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./no_signal.jpg"))

    def run(self):
        threading.Thread(target=self.fetch, daemon=True, args=()).start()
        
    def fetch_status(self):
        self.flag = False if self.flag else True

    def fetch(self):
        while True:
            with self.lock:
                self.status, img = self.source.read()
                self.img = cv2.resize(img, [1280, 720], interpolation = cv2.INTER_AREA)
                self.last_frame = time.time()

    def getentrance_name(self):
        return self.entrance_name
    
    def getimg(self):
        if (self.status is not None) and (self.img is not None):
            return self.img.copy(), self.last_frame, True
        else:
            return self.nosignal, self.last_frame, False