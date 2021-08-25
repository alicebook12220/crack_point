import threading
import cv2
import time
import numpy as np

net = cv2.dnn_DetectionModel('cfg/custom-yolov4-tiny.cfg', 'backup/custom-yolov4-tiny_last.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net.setInputSize(1024, 768)
net.setInputScale(1.0 / 255)
net.setInputSwapRB(True)

img = cv2.imread("img/2021-04-27_2.jpg")
start = time.time()
classes, confidences, boxes = net.detect(img, confThreshold=0.1, nmsThreshold=0.5)
end = time.time()
print("cam3_first:", end - start)
for i in range(1000):
    start = time.time()
    classes, confidences, boxes = net.detect(img, confThreshold=0.1, nmsThreshold=0.5)
    end = time.time()
    print("cam3:", i, end - start, len(boxes))

