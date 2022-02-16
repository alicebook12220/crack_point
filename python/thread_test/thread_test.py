import threading
import cv2
import time
import datetime
import numpy as np
import os
'''
net1 = cv2.dnn_DetectionModel('cfg/custom-yolov4-tiny.cfg', 'backup/custom-yolov4-tiny_last.weights')
net1.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net1.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net1.setInputSize(1024, 768)
net1.setInputScale(1.0 / 255)
net1.setInputSwapRB(True)
net2 = cv2.dnn_DetectionModel('cfg/custom-yolov4-tiny.cfg', 'backup/custom-yolov4-tiny_2.weights')
net2.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net2.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net2.setInputSize(1024, 768)
net2.setInputScale(1.0 / 255)
net2.setInputSwapRB(True)
net3 = cv2.dnn_DetectionModel('cfg/custom-yolov4-tiny.cfg', 'backup/custom-yolov4-tiny_last.weights')
net3.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net3.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net3.setInputSize(1024, 768)
net3.setInputScale(1.0 / 255)
net3.setInputSwapRB(True)
net4 = cv2.dnn_DetectionModel('cfg/custom-yolov4-tiny.cfg', 'backup/custom-yolov4-tiny_last.weights')
net4.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net4.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net4.setInputSize(1024, 768)
net4.setInputScale(1.0 / 255)
net4.setInputSwapRB(True)
classes, confidences, boxes = net1.detect(img, confThreshold=0.1, nmsThreshold=0.5) #0.9s
classes, confidences, boxes = net2.detect(img, confThreshold=0.1, nmsThreshold=0.5) #0.9s
classes, confidences, boxes = net3.detect(img, confThreshold=0.1, nmsThreshold=0.5) #0.9s
classes, confidences, boxes = net4.detect(img, confThreshold=0.1, nmsThreshold=0.5) #0.9s
'''
def checkThread(sleeptimes=1, initThreadsName=[]):
    for i in range(0,10):
        nowThreadsName=[]#用来保存執行緒名稱
        now=threading.enumerate()#得到目前執行緒名稱
        for i in now:
            nowThreadsName.append(i.getName())
        #print(nowThreadsName)
        #print(initThreadsName)
        for cam in initThreadsName:
            if cam in nowThreadsName:
                #多執行緒還在，繼續執行
                pass
            else:
                #多執行緒不在，重新啟動
                print('===' + cam,'stopped，now restart')
                t=threading.Thread(target=printIP,args=(cam,))#重启线程
                t.setName(cam)#重设name
                t.start()
        
        time.sleep(sleeptimes)#隔一段时间重新运行，检测有没有线程down

def thread_cam1():
    #image = cv2.imread(path)
    #classes, confidences, boxes = net1.detect(image, confThreshold=0.1, nmsThreshold=0.5) #0.9s
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("1:", now)
    #os.system("python cam1.py")
    
def thread_cam2():
    #image = cv2.imread(path)
    #classes, confidences, boxes = net2.detect(image, confThreshold=0.1, nmsThreshold=0.5) #0.9s
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("2:", now)
    #os.system("python cam2.py")

def thread_cam3():
    #image = cv2.imread(path)
    #classes, confidences, boxes = net3.detect(image, confThreshold=0.1, nmsThreshold=0.5) #0.9s
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("3:", now)
    #os.system("python cam3.py")

def thread_cam4():
    #image = cv2.imread(path)
    #classes, confidences, boxes = net4.detect(image, confThreshold=0.1, nmsThreshold=0.5) #0.9s
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("4:", now)
    #os.system("python cam4.py")

def thread_cam5():
    #image = cv2.imread(path)
    #classes, confidences, boxes = net4.detect(image, confThreshold=0.1, nmsThreshold=0.5) #0.9s
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("5:", now)
    #os.system("python cam5.py")

def thread_cam6():
    #image = cv2.imread(path)
    #classes, confidences, boxes = net4.detect(image, confThreshold=0.1, nmsThreshold=0.5) #0.9s
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("6:", now)
    #os.system("python cam6.py")

def printIP(ip):
    print(ip)

list_cam=['cam1','cam2','cam3', 'cam4'] #

cam1 = threading.Thread(target = thread_cam1)
cam2 = threading.Thread(target = thread_cam2)
cam3 = threading.Thread(target = thread_cam3)
cam4 = threading.Thread(target = thread_cam4)
cam5 = threading.Thread(target = thread_cam5)
cam6 = threading.Thread(target = thread_cam6)
start = time.time()
'''
cam1.start()
cam2.start()
cam3.start()
cam4.start()
cam5.start()
cam6.start()
'''
threads=[]
initThreadsName=[] #初始化相機執行緒名稱
for cam in list_cam:
    initThreadsName.append(cam)
    t=threading.Thread(target=printIP,args=(cam,))
    t.setName(cam)
    threads.append(t)
    
for t in threads:
    t.start()

check = threading.Thread(target = checkThread, args=(1, initThreadsName))
check.setName('Thread:check')
check.start()
#cam1.join()
#cam2.join()
#cam3.join()
#cam4.join()

#print("all time:", time.time() - start)
