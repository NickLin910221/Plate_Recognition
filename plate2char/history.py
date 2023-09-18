import datetime
from datetime import timezone, timedelta

class Plate:
    __slots__ = ["img", "xmin", "ymin", "xmax", "ymax", "number", "timestamp", "entrance"]

    def __init__(self, img, entrance, xmin = 0, ymin = 0, xmax = 0, ymax = 0) -> None:
        self.img = img
        self.timestamp = datetime.datetime.now(timezone(timedelta(hours=+8))).strftime("%Y-%m-%dT%H:%M:%S")
        self.entrance = entrance

    def write_number(self, number):
        self.number = number

    def set_plate(self, xmin = 0, ymin = 0, xmax = 0, ymax = 0):
        self.xmin = int(xmin)
        self.xmax = int(xmax)
        self.ymin = int(ymin)
        self.ymax = int(ymax)

    def get_plate_number(self):
        return f'{self.number}'
    
    def get_ts(self):
        return f'{self.timestamp}'
    
    def get_entrance(self):
        return f'{self.entrance}'