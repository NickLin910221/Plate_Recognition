import os
import torch
import cv2

img = cv2.imread(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"./AQM6955.jpg"))

abs_path = os.path.dirname(os.path.abspath(__file__)) + "/"
model_plate = torch.hub.load(abs_path + 'yolov5_plate_v5m', 'custom', path = abs_path + 'yolov5_plate_v5m/runs/train/exp/weights/best.pt', source='local')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_plate.to(device)

res = model_plate(img)

print(res.xyxy[0])