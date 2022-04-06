from teli import *
import cv2
import numpy as np
import time
import datetime
import glob
import os
import ftplib
import csv
import pymcprotocol
import threading
import matplotlib.pyplot as plt
from matplotlib import font_manager
#import PLC

host = "192.168.3.100"
username = "ftpuser"
password = "ftp@12345678"
station_name = "RUB_crack"
predict_path = "C:/Users/user/Desktop/" + station_name

device = None
in_sensor = None
speed_sensor = None
exist_glass = None
glass_mode = None
img_1 = None
img_2 = None
img_3 = None
img_4 = None

def plc_connect():
	global device
	while True:
		try:
			device = pymcprotocol.Type3E(plctype="Q")
			device.setaccessopt(commtype="binary") #binary, ascii
			device.connect("192.168.30.33", 5002)
			print('PLC連線成功')
			break
		except:
			print('PLC連線失敗')
			pass


def plc_read():
    global device
    global in_sensor
    #global speed_sensor
    global exist_glass
    global glass_mode
    try:
        if device is not None:
            in_sensor = device.batchread_bitunits(headdevice="B1803", readsize=1)[0]  # batchread_wordunits
            #speed_sensor = device.batchread_wordunits(headdevice="W1830", readsize=1)[0]
            exist_glass = device.batchread_bitunits(headdevice="B1802", readsize=1)[0]
            glass_mode = device.batchread_wordunits(headdevice="W1216", readsize=1)[0]
            #print("在籍B1802:", exist_glass)
            #print("開始B1803:", in_sensor)
            #print("種類W1236:", glass_mode)
            #if glass_mode == 0 or glass_mode == 2:
            #    print(6666)
    except:
        print('連線中斷，PLC嘗試重新連線')
        device = None
        plc_connect()

def plc_write(defect_sum):
    global device
    try:
        if defect_sum > 0:
            #device.batchwrite_bitunits(headdevice="B1025", values=[1])
            print('停機')
        else:
            #device.batchwrite_bitunits(headdevice="B1025", values=[0])
            print('保持啟動')
    except:
        print('PLC寫入失敗')

def ftp_upload(file_path, ftp_path):
    print("ftp upload:", ftp_path)
    ftp_session = ftplib.FTP(host)
    ftp_session.login(username, password)
    file = open(file_path, 'rb')
    ftp_session.storbinary('STOR ' + ftp_path, file)
    file.close()
    ftp_session.quit()


def csv_write(mode="header", today="test", result=0, camera_name="camera_1"):
    print("csv mode:", mode, camera_name)
    data = ""
    if mode == "header":
        data = ['datetime', 'result']
    else:
        now = datetime.datetime.now().strftime("%Y%m%d %H%M%S")
        data = [now, result]

    with open(predict_path + "/" + today + '/log/' + today + "_" + camera_name + '_result.csv', 'a', encoding='UTF8',
              newline='') as f:
        writer = csv.writer(f)
        # write the data
        writer.writerow(data)
        
def point_map(map_path="", end_x="", point_x="", width=768, point_y=0, cam_num=1):
    point_y = (width - point_y) + width*abs(cam_num-3)
    point_y = int((point_y/(width*4))*600)
    point_x = int((point_x/end_x)*740)
    
    point_map = np.zeros((600,740,3), dtype=np.uint8)
    point_map[::]=191
    cv2.line(point_map, (0,500), (50,600), (0,0,255), 2)
    cv2.putText(point_map, "1500mm", (5,300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
    cv2.putText(point_map, "1850mm", (340,590), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
    cv2.putText(point_map, "("+str(int(point_x/740*1850))+", "+str(1500-int(point_y/600*1500))+")", (point_x,point_y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 1, cv2.LINE_AA)
    cv2.circle(point_map, (point_x, point_y), 10, (255,0,0), -1)
    cv2.imwrite(map_path, point_map)
    return point_map
    
def loda_model():
    net = cv2.dnn_DetectionModel(
        'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/cfg/custom-yolov4-3l-tiny.cfg',
        'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/backup/custom-yolov4-3l-tiny_last_95.78.weights')
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
    net.setInputSize(1024, 768)
    net.setInputScale(1.0 / 255)
    net.setInputSwapRB(True)
    return net

def checkThread(sleeptimes=1, initThreadsName=[]):
    global cameras
    while(True):
        nowThreadsName=[]#用来保存執行緒名稱
        now=threading.enumerate()#得到目前執行緒名稱
        for i in now:
            nowThreadsName.append(i.getName())
        #print(nowThreadsName)
        #print(initThreadsName)
        for cam_id in initThreadsName:
            if cam_id[0] in nowThreadsName:
                #多執行緒還在，繼續執行
                pass
            else:
                #多執行緒不在，重新啟動
                #cameras = getNumOfCameras()
                print('---', cam_id, 'stopped，now restart')
                t=threading.Thread(target=crack_camera,args=(cam_id[0], cam_id[1],))#重啟多執行緒
                t.setName(cam_id[0])#重設name
                t.start()
                
        time.sleep(sleeptimes)#

def PLC_RUN():
    print("PLC READ")
    while True:
        plc_read()

def crack_camera(camera_id, cam_number):
    global device
    global in_sensor
    global speed_sensor
    global exist_glass
    global glass_mode
    global img_1
    global img_2
    global img_3
    global img_4
    #cameras = getNumOfCameras()
    net = loda_model()
    mask_left_top = (0, 70)
    mask_right_top = (1023, 70)
    mask_right_down = (0,70)
    mask_left_down = (0,70)
    if camera_id == "0510116":
        camera_name = "camera_1" #1
        mask_left_top = (0, 300)
        mask_right_top = (1023, 300)
        mask_right_down = (1023,600)
        mask_left_down = (0,600)
    elif camera_id == "0510055":
        camera_name = "camera_2" #3
        mask_left_top = (0, 350)
        mask_right_top = (1023, 350)
        mask_right_down = (1023,650)
        mask_left_down = (0,650)
    elif camera_id == "0510113":
        camera_name = "camera_3" #2
        mask_left_top = (0, 200)
        mask_right_top = (1023, 200)
        mask_right_down = (1023,500)
        mask_left_down = (0,500)
    elif camera_id == "0510122":
        camera_name = "camera_4" #0
        mask_left_top = (0, 200)
        mask_right_top = (1023, 200)
        mask_right_down = (1023,500)
        mask_left_down = (0,500)
    glass_con_count = 0  # 連續玻璃數量
    glass_count = 0  # 玻璃數量
    glass_start = False
    map_save = False
    # fps_camera = 15 #相機FPS
    # width, height = image.size
    # 裂點容許數量
    min1_crack_count = 2
    min5_crack_count = 3
    # 裂點同一位置容許寬度 越大越敏感
    crack_width = 2
    #邊角反射容許寬度
    cor_width = 3
    # 產生警戒區域遮罩
    warn_mask = np.zeros((768, 1024), dtype=np.uint8)
    # 雷射光遮罩左上 右上 右下 左下
    roi_corners = np.array([[mask_left_top, mask_right_top, mask_right_down, mask_left_down]], dtype=np.int32)
    channel_count = 1
    ignore_mask_color = (255,) * channel_count
    cv2.fillPoly(warn_mask, roi_corners, ignore_mask_color)
    #裂點MAP圖相關參數
    start_time = ""
    point_time = ""
    end_time = ""
    x_center = 0
    #PLC連線
    #plc_connect()
    # time_temp = str(datetime.date.today())
    if (cameras):
        # Connect to Pekat
        # pekat = Pekat(host = "127.0.0.1", port = 8100, already_running = True)
        with Camera(cam_number) as cam:
            # How to get and set properties
            # String
            # print(cam.getStringValue("DeviceUserID"))
            # cam.setStringValue("DeviceUserID", "My camera")
            # Enum 圖像模式
            # print(cam.getEnumStringValue("TestPattern"))
            # cam.setEnumStringValue("TestPattern", "Off")
            # Int 偵數
            print("Frame Count:", cam.getIntValue("AcquisitionFrameCount"))
            cam.setIntValue("AcquisitionFrameCount", 15)
            # Float 曝光時間
            print("Exposure Time:", cam.getFloatValue("ExposureTime"))
            cam.setFloatValue("ExposureTime", 5000)
            print("Gain:", cam.getFloatValue("Gain"))
            # cam.setFloatValue("Gain", 24.0)

            # Start streaming
            cam.startStream()
            # Wait for image 2000ms
            w = cam.waitForImage(2000)
            # csv_time = time.time()
            if (w):
                min1_defectContinue = []
                min5_defectHave = []
                min1_count = []  # 記錄裂點個數和是否同片
                min5_count = []
                time_OK = time.time()
                OK_save = False
                while (True):
                    #plc_read()
                    today = str(datetime.date.today())
                    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    # Image received
                    img = cam.getCurrentImage()
                    if camera_name == "camera_1":
                        img_1 = cv2.resize(img, (640, 480))
                    elif camera_name == "camera_2":
                        img_2 = cv2.resize(img, (640, 480))
                    elif camera_name == "camera_3":
                        img_3 = cv2.resize(img, (640, 480))
                    elif camera_name == "camera_4":
                        img_4 = cv2.resize(img, (640, 480))
                    #cv2.imshow(camera_name, imshow)

                    output_path = predict_path + "/" + today
                    isExists = os.path.exists(output_path)
                    if not isExists:
                        # print("建立日期目錄:", today)
                        # os.makedirs(output_path)
                        os.makedirs(output_path + "/OK/")
                        # os.makedirs(output_path + "NG/")
                        os.makedirs(output_path + "/NG/box")
                        os.makedirs(output_path + "/NG/nobox")
                        os.makedirs(output_path + '/log')
                    isExists = os.path.exists(
                        predict_path + "/" + today + '/log/' + today + "_" + camera_name + '_result.csv')
                    if not isExists:
                        csv_write("header", today, 0, camera_name)
                    # predict
                    image = cv2.resize(img, (1024, 768))
                    image_nobox = image.copy()
                    # image_light = image[warn_mask == 255]
                    # image_light = np.mean(image_light)

                    # print("image_light:",image_light)
                    # if image_light > 1 and image_light < 20:
                    alarm_status = False
                    defect_sum = 0
                    #print(exist_glass, in_sensor)
                    if exist_glass == 1 and in_sensor == 1 and glass_mode == 1:
                        if not glass_start:
                            print(camera_name + "取像開始")
                            glass_start = True
                            OK_save = True
                            time_OK = time.time()
                            start_time = time.time()
                        classes, confidences, boxes = net.detect(image, confThreshold=0.80, nmsThreshold=0.5)
                        if len(boxes) > 0:
                            for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
                                pstring = str(int(100 * confidence)) + "%"
                                x_left, y_top, width, height = box

                                boundingBox = [
                                    (x_left, y_top),  # 左上頂點
                                    (x_left, y_top + height),  # 左下頂點
                                    (x_left + width, y_top + height),  # 右下頂點
                                    (x_left + width, y_top)  # 右上頂點
                                ]
                                rectColor = (0, 0, 255)
                                textCoord = (x_left, y_top - 10)
                                # 在影像中標出Box邊界和類別、信心度
                                cv2.rectangle(image, boundingBox[0], boundingBox[2], rectColor, 2)
                                cv2.putText(image, pstring, textCoord, cv2.FONT_HERSHEY_DUPLEX, 1, rectColor, 2)

                                x_center = x_left + int(width / 2)
                                y_center = y_top + int(height / 2)
                                '''
                                #過濾邊角反射
                                if abs(x_center - 229) < cor_width or abs(x_center - 289) < cor_width or abs(x_center - 196) < cor_width or abs(x_center - 964) < cor_width or abs(x_center - 393) < cor_width or abs(x_center - 770) < cor_width or abs(x_center - 583) < cor_width or abs(x_center - 205) < cor_width or abs(x_center - 154) < cor_width or abs(x_center - 113) < cor_width or abs(x_center - 890) < cor_width:
                                    print("邊角反射跳過")
                                    continue
                                '''
                                # 檢查瑕疵是否在光帶上
                                if warn_mask[y_center][x_center] == 255:
                                    # print("on laser line")
                                    # 檢查瑕疵是否在同一位置出現(連續3片)
                                    if not min1_defectContinue:
                                        print(camera_name + "連續片有point")
                                        min1_defectContinue.append(x_center)
                                        min1_count.append([1, 1, time.time()])
                                    else:
                                        # 判斷裂點是否在相同位置(連續3片)
                                        is_crack = False
                                        crack_same = False
                                        for i in range(len(min1_defectContinue)):
                                            if abs(x_center - min1_defectContinue[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min1_count[i][1] == 1:
                                                    #出現間隔大於1秒
                                                    if time.time()-min1_count[i][2] > 1:
                                                        print(camera_name + "連續片-同位置出現point: ",i)
                                                        min1_count[i][0] = min1_count[i][0] - 1
                                                        min1_count[i][2] = time.time()
                                                    crack_same = True
                                                    break
                                                else:
                                                    min1_count[i][1] = 1
                                                is_crack = True
                                                min1_count[i][0] = min1_count[i][0] + 1
                                                print(camera_name + "連續片 location:", i, "crack count:", min1_count[i][0])
                                                break
                                        if not is_crack and not crack_same:
                                            min1_defectContinue.append(x_center)
                                            min1_count.append([1, 1, time.time()])
                                    # 判斷相同位置裂點是否大於2個(連續3片)
                                    if glass_con_count < 3:
                                        defect_sum = sum(i[0] > min1_crack_count for i in min1_count)
                                        if defect_sum > 0:
                                            point_time = time.time()
                                            # 發報
                                            alarm_status = True
                                            min1_defectContinue.clear()
                                            min5_defectHave.clear()
                                            min1_count.clear()
                                            min5_count.clear()
                                            plc_write(defect_sum)
                                            print(camera_name + "連續片 Alarm")
                                            break
                                    else:
                                        min1_defectContinue.clear()
                                        min1_count.clear()
                                    
                                    # 檢查瑕疵是否在同一位置出現(10片)
                                    if not min5_defectHave:
                                        print(camera_name + "非連續片有point")
                                        min5_defectHave.append(x_center)
                                        min5_count.append([1, 1, time.time()])
                                    else:
                                        # 判斷裂點是否在相同位置(10片)
                                        is_crack = False
                                        crack_same = False
                                        for i in range(len(min5_defectHave)):
                                            if abs(x_center - min5_defectHave[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min5_count[i][1] == 1:
                                                    #間隔大於1秒
                                                    if time.time()-min5_count[i][2] > 1:
                                                        print(camera_name + "非連續片-同位置出現point: ",i)
                                                        min5_count[i][0] = min5_count[i][0] - 1
                                                        min5_count[i][2] = time.time()
                                                    crack_same = True
                                                    break
                                                else:
                                                    min5_count[i][1] = 1
                                                is_crack = True
                                                min5_count[i][0] = min5_count[i][0] + 1
                                                print(camera_name + "非連續片 location:", i, "crack count:", min5_count[i][0])
                                                break
                                        if not is_crack and not crack_same:
                                            min5_defectHave.append(x_center)
                                            min5_count.append([1, 1, time.time()])
                                    # 判斷相同位置裂點是否大於4個(5分鐘)
                                    if glass_count < 10:
                                        defect_sum = sum(i[0] > min5_crack_count for i in min5_count)
                                        if defect_sum > 0:
                                            point_time = time.time()
                                            # 發報
                                            alarm_status = True
                                            min1_defectContinue.clear()
                                            min5_defectHave.clear()
                                            min1_count.clear()
                                            min5_count.clear()
                                            plc_write(defect_sum)
                                            print(camera_name + "非連續片 Alarm")
                                            break
                                    else:
                                        min5_defectHave.clear()
                                        min5_count.clear()
                            # 如果Alarm，存圖並上傳到FTP Server
                            if alarm_status:
                                map_save = True
                                csv_write("NG", today, 1, camera_name)
                                csv_path = predict_path + "/" + today + '/log/' + today + "_" + camera_name + '_result.csv'
                                img_box_path = output_path + "/NG/box/" + now + "_" + camera_name + ".jpg"
                                img_nobox_path = output_path + "/NG/nobox/" + now + "_" + camera_name + ".jpg"
                                cv2.imwrite(img_box_path, image)
                                cv2.imwrite(img_nobox_path, image_nobox)
                                # NG_img_count = NG_img_count + 1
                                cv2.imshow('crack_' + camera_name, image)
                                
                                try:
                                    ftp_path = "RUB_crack/image/box/" + now + "_" + camera_name + ".jpg"
                                    ftp_upload(img_box_path, ftp_path)
                                    ftp_path = "RUB_crack/image/nobox/" + now + "_" + camera_name + ".jpg"
                                    ftp_upload(img_nobox_path, ftp_path)
                                    ftp_path = "RUB_crack/log/" + today + "_" + camera_name + ".csv"
                                    ftp_upload(csv_path, ftp_path)
                                except:
                                    print("ftp server connect error")
                                    pass
                                
                        else:
                            if time.time() - time_OK > 5 and OK_save:
                                OK_save = False
                                # cv2.imshow('crack', image)
                                output_path = predict_path + "/" + today
                                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                cv2.imwrite(output_path + "/OK/" + now + ".jpg", image)
                    else:
                        
                        if glass_start:
                            print(camera_name + "取像結束")
                            glass_start = False
                            glass_count = glass_count + 1
                            glass_con_count = glass_con_count + 1
                            
                            if glass_con_count >= 3:
                                glass_con_count = 0
                                min1_defectContinue.clear()
                                min1_count.clear()
                            if glass_count >= 10:
                                glass_count = 0
                                min5_defectHave.clear()
                                min5_count.clear()
                            # 重置裂點同片玻璃記錄
                            for i in range(len(min1_count)):
                                min1_count[i][1] = 0
                            for i in range(len(min5_count)):
                                min5_count[i][1] = 0

                            if not alarm_status:
                                csv_time = time.time()
                                csv_write("OK", today, 0, camera_name)
                                csv_path = predict_path + "/" + today + '/log/' + today + "_" + camera_name + '_result.csv'
                                try:
                                    ftp_path = "RUB_crack/log/" + today + "_" + camera_name + ".csv"
                                    ftp_upload(csv_path, ftp_path)
                                except:
                                    print("ftp server connect error")
                                    pass
                            if map_save:
                                map_save = False
                                #產生裂點MAP
                                end_time = int(time.time() - start_time)
                                point_time = int(point_time - start_time)
                                map_path = predict_path + "/" + today + '/log/' + now + '_point_map.jpg'
                                crack_map = point_map(map_path, end_time, point_time, image.shape[1], x_center, cam_number)
                                #ftp_path = "RUB_crack/point_map/" + now + '_point_map.jpg'
                                #ftp_upload(map_path, ftp_path)
                                cv2.imshow("crack map_" + camera_name, crack_map)
                                key = cv2.waitKey(1)
                            plc_write(defect_sum)
                    
                    # Stop streaming
                    
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        cv2.destroyAllWindows()
                        cam.stopStream()
                        break
                    #print(time.time()-test_time) 0.031s
            else:
                print("Image not received in time")

initialize()
cameras = getNumOfCameras()
list_cam=[]
print("Number of cameras: %d" % cameras)
plc_connect()
if (cameras):
    for i in range(cameras):
        info = getCameraInfo(i)
        print("Camera %d" % i)
        print("  Camera type: %s" % info.camType)
        print("  Manufacturer: %s" % info.manufacturer)
        print("  Model: %s" % info.modelName)
        print("  Serial no: %s" % info.serialNumber)
        print("  User name: %s" % info.userDefinedName)
        list_cam.append(info.serialNumber)
#使用多執行緒
#list_cam=['camera_1','camera_2','camera_3', 'camera_4']
threads=[]
initThreadsName=[] #初始化相機執行緒名稱
cam_idx = 0
for cam_id in list_cam:
    initThreadsName.append([cam_id, cam_idx])
    t=threading.Thread(target=crack_camera,args=(cam_id, cam_idx,))
    t.setName(cam_id)
    threads.append(t)
    cam_idx += 1 

PLC = threading.Thread(target = PLC_RUN)
PLC.setName('PLC')
PLC.start()

for t in threads:
    t.start()

check = threading.Thread(target = checkThread, args=(1, initThreadsName))
check.setName('Thread:check')
check.start()

time.sleep(5)
while(True):
    cv2.imshow("camera_1", img_1)
    key = cv2.waitKey(10)
    cv2.imshow("camera_2", img_2)
    key = cv2.waitKey(10)
    cv2.imshow("camera_3", img_3)
    key = cv2.waitKey(10)
    cv2.imshow("camera_4", img_4)
    key = cv2.waitKey(10)
    
