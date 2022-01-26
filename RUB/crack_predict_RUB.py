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
            print('PLC寫入成功:停機')
        else:
            device.batchwrite_bitunits(headdevice="B1025", values=[0])
            print('PLC寫入成功:保持啟動')
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
    my_font = font_manager.FontProperties(fname=r"C:\Windows\Fonts\msjhbd.ttc", size=18) #微軟正黑體(粗)
    plt.style.use("ggplot")     # 使用ggplot主題樣式
    plt.xlabel("玻璃長度(以時間計算)", fontproperties=my_font)  #設定x座標標題
    plt.ylabel("玻璃寬度(以像素計算)", fontproperties=my_font)  #設定y座標標題
    plt.title("玻璃裂點位置圖", fontproperties=my_font)        #設定標題
    plt.xlim(0, end_x)
    plt.ylim(0, width*4)
    
    plt.scatter(point_x,     # x軸資料
                point_y*cam_num,     # y軸資料
                c = "m",     # 點顏色
                s = 50,      # 點大小
                alpha = .5,  # 透明度
                marker = "D")   # 點樣式
    print("point map save:", map_path)
    plt.savefig(map_path)   #儲存圖檔
    plt.close()      # 關閉圖表

net = cv2.dnn_DetectionModel(
    'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/cfg/custom-yolov4-3l-tiny.cfg',
    'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/backup/custom-yolov4-tiny_last.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net.setInputSize(1024, 768)
net.setInputScale(1.0 / 255)
net.setInputSwapRB(True)

net2 = cv2.dnn_DetectionModel(
    'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/cfg/custom-yolov4-3l-tiny.cfg',
    'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/backup/custom-yolov4-tiny_last.weights')
net2.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net2.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net2.setInputSize(1024, 768)
net2.setInputScale(1.0 / 255)
net2.setInputSwapRB(True)

net3 = cv2.dnn_DetectionModel(
    'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/cfg/custom-yolov4-3l-tiny.cfg',
    'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/backup/custom-yolov4-tiny_last.weights')
net3.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net3.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net3.setInputSize(1024, 768)
net3.setInputScale(1.0 / 255)
net3.setInputSwapRB(True)

net4 = cv2.dnn_DetectionModel(
    'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/cfg/custom-yolov4-3l-tiny.cfg',
    'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/backup/custom-yolov4-tiny_last.weights')
net4.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net4.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net4.setInputSize(1024, 768)
net4.setInputScale(1.0 / 255)
net4.setInputSwapRB(True)

initialize()
cameras = getNumOfCameras()
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

def PLC_RUN():
    print("PLC READ")
    while True:
        plc_read()

def crack_camera1():
    global device
    global in_sensor
    global speed_sensor
    global exist_glass
    global glass_mode
    camera_name = "camera_1"
    cam_number = 1
    glass_con_count = 0  # 連續玻璃數量
    glass_count = 0  # 玻璃數量
    glass_start = False
    map_save = False
    map_now = ""
    # fps_camera = 15 #相機FPS
    # width, height = image.size
    # 裂點容許數量
    min1_crack_count = 2
    min5_crack_count = 4
    # 裂點同一位置容許寬度
    crack_width = 2
    #邊角反射容許寬度
    cor_width = 3
    # 產生警戒區域遮罩
    warn_mask = np.zeros((768, 1024), dtype=np.uint8)
    # 雷射光遮罩左上 右上 右下 左下
    roi_corners = np.array([[(0, 70), (1023, 70), (1023, 95), (0, 95)]], dtype=np.int32)
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
        with Camera(1) as cam:
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
                    # Image received
                    img = cam.getCurrentImage()
                    imshow = cv2.resize(img, (640, 480))
                    cv2.imshow(camera_name, imshow)

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
                                #過濾邊角反射
                                if abs(x_center - 229) < cor_width or abs(x_center - 289) < cor_width or abs(x_center - 196) < cor_width or abs(x_center - 964) < cor_width or abs(x_center - 393) < cor_width or abs(x_center - 770) < cor_width or abs(x_center - 583) < cor_width or abs(x_center - 205) < cor_width or abs(x_center - 154) < cor_width or abs(x_center - 113) < cor_width or abs(x_center - 890) < cor_width:
                                    print("邊角反射跳過")
                                    continue
                                # 檢查瑕疵是否在光帶上
                                if warn_mask[y_center][x_center] == 255:
                                    # print("on laser line")
                                    # 檢查瑕疵是否在同一位置出現(1分鐘)
                                    if not min1_defectContinue:
                                        print(camera_name + "連續片 first")
                                        min1_defectContinue.append(x_center)
                                        min1_count.append([1, 1])
                                    else:
                                        # 判斷裂點是否在相同位置(1分鐘)
                                        is_crack = False
                                        for i in range(len(min1_defectContinue)):
                                            if abs(x_center - min1_defectContinue[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min1_count[i][1] == 1:
                                                    break
                                                else:
                                                    min1_count[i][1] = 1
                                                is_crack = True
                                                min1_count[i][0] = min1_count[i][0] + 1
                                                print(camera_name + "連續片 location", i, "crack count:", min1_count[i][0])
                                                break
                                        if not is_crack:
                                            min1_defectContinue.append(x_center)
                                            min1_count.append([1, 1])
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
                                    if not min5_defectHave:
                                        print(camera_name + "非連續片 first")
                                        min5_defectHave.append(x_center)
                                        min5_count.append([1, 1])
                                    else:
                                        # 判斷裂點是否在相同位置(5分鐘)
                                        is_crack = False
                                        for i in range(len(min5_defectHave)):
                                            if abs(x_center - min5_defectHave[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min5_count[i][1] == 1:
                                                    break
                                                else:
                                                    min5_count[i][1] = 1
                                                is_crack = True
                                                min5_count[i][0] = min5_count[i][0] + 1
                                                print(camera_name + "非連續片 location", i, "crack count:", min5_count[i][0])
                                                break
                                        if not is_crack:
                                            min5_defectHave.append(x_center)
                                            min5_count.append([1, 1])
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
                                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                map_now = now
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
                                map_path = predict_path + "/" + today + '/log/' + map_now + '_point_map.jpg'
                                point_map(map_path, end_time, point_time, image.shape[1], x_center, cam_number)
                                ftp_path = "RUB_crack/point_map/" + now + '_point_map.jpg'
                                ftp_upload(map_path, ftp_path)
                                
                            plc_write(defect_sum)

                    # Stop streaming
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        cv2.destroyAllWindows()
                        cam.stopStream()
                        break
            else:
                print("Image not received in time")

    terminate()

def crack_camera2():
    global device
    global in_sensor
    global speed_sensor
    global exist_glass
    global glass_mode
    camera_name = "camera_2"
    cam_number = 2
    glass_con_count = 0  # 連續玻璃數量
    glass_count = 0  # 玻璃數量
    glass_start = False
    map_save = False
    map_now = ""
    # fps_camera = 15 #相機FPS
    # width, height = image.size
    # 裂點容許數量
    min1_crack_count = 2
    min5_crack_count = 4
    # 裂點同一位置容許寬度
    crack_width = 2
    #邊角反射容許寬度
    cor_width = 3
    # 產生警戒區域遮罩
    warn_mask = np.zeros((768, 1024), dtype=np.uint8)
    # 雷射光遮罩左上 右上 右下 左下
    roi_corners = np.array([[(0, 70), (1023, 70), (1023, 95), (0, 95)]], dtype=np.int32)
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
        with Camera(3) as cam:
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
                    # Image received
                    img = cam.getCurrentImage()
                    imshow = cv2.resize(img, (640, 480))
                    cv2.imshow(camera_name, imshow)

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
                        classes, confidences, boxes = net2.detect(image, confThreshold=0.80, nmsThreshold=0.5)
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
                                #過濾邊角反射
                                if abs(x_center - 229) < cor_width or abs(x_center - 289) < cor_width or abs(x_center - 196) < cor_width or abs(x_center - 964) < cor_width or abs(x_center - 393) < cor_width or abs(x_center - 770) < cor_width or abs(x_center - 583) < cor_width or abs(x_center - 205) < cor_width or abs(x_center - 154) < cor_width or abs(x_center - 113) < cor_width or abs(x_center - 890) < cor_width:
                                    print("邊角反射跳過")
                                    continue
                                # 檢查瑕疵是否在光帶上
                                if warn_mask[y_center][x_center] == 255:
                                    # print("on laser line")
                                    # 檢查瑕疵是否在同一位置出現(1分鐘)
                                    if not min1_defectContinue:
                                        print(camera_name + "連續片 first")
                                        min1_defectContinue.append(x_center)
                                        min1_count.append([1, 1])
                                    else:
                                        # 判斷裂點是否在相同位置(1分鐘)
                                        is_crack = False
                                        for i in range(len(min1_defectContinue)):
                                            if abs(x_center - min1_defectContinue[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min1_count[i][1] == 1:
                                                    break
                                                else:
                                                    min1_count[i][1] = 1
                                                is_crack = True
                                                min1_count[i][0] = min1_count[i][0] + 1
                                                print(camera_name + "連續片 location", i, "crack count:", min1_count[i][0])
                                                break
                                        if not is_crack:
                                            min1_defectContinue.append(x_center)
                                            min1_count.append([1, 1])
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
                                    if not min5_defectHave:
                                        print(camera_name + "非連續片 first")
                                        min5_defectHave.append(x_center)
                                        min5_count.append([1, 1])
                                    else:
                                        # 判斷裂點是否在相同位置(5分鐘)
                                        is_crack = False
                                        for i in range(len(min5_defectHave)):
                                            if abs(x_center - min5_defectHave[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min5_count[i][1] == 1:
                                                    break
                                                else:
                                                    min5_count[i][1] = 1
                                                is_crack = True
                                                min5_count[i][0] = min5_count[i][0] + 1
                                                print(camera_name + "非連續片 location", i, "crack count:", min5_count[i][0])
                                                break
                                        if not is_crack:
                                            min5_defectHave.append(x_center)
                                            min5_count.append([1, 1])
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
                                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                map_now = now
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
                                map_path = predict_path + "/" + today + '/log/' + map_now + '_point_map.jpg'
                                point_map(map_path, end_time, point_time, image.shape[1], x_center, cam_number)
                                ftp_path = "RUB_crack/point_map/" + now + '_point_map.jpg'
                                ftp_upload(map_path, ftp_path)
                                
                            plc_write(defect_sum)

                    # Stop streaming
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        cv2.destroyAllWindows()
                        cam.stopStream()
                        break
            else:
                print("Image not received in time")

    terminate()

def crack_camera3():
    global device
    global in_sensor
    global speed_sensor
    global exist_glass
    global glass_mode
    camera_name = "camera_3"
    cam_number = 3
    glass_con_count = 0  # 連續玻璃數量
    glass_count = 0  # 玻璃數量
    glass_start = False
    map_save = False
    map_now = ""
    # fps_camera = 15 #相機FPS
    # width, height = image.size
    # 裂點容許數量
    min1_crack_count = 2
    min5_crack_count = 4
    # 裂點同一位置容許寬度
    crack_width = 2
    #邊角反射容許寬度
    cor_width = 3
    # 產生警戒區域遮罩
    warn_mask = np.zeros((768, 1024), dtype=np.uint8)
    # 雷射光遮罩左上 右上 右下 左下
    roi_corners = np.array([[(0, 70), (1023, 70), (1023, 95), (0, 95)]], dtype=np.int32)
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
        with Camera(2) as cam:
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
                    # Image received
                    img = cam.getCurrentImage()
                    imshow = cv2.resize(img, (640, 480))
                    cv2.imshow(camera_name, imshow)

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
                        classes, confidences, boxes = net3.detect(image, confThreshold=0.80, nmsThreshold=0.5)
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
                                #過濾邊角反射
                                if abs(x_center - 229) < cor_width or abs(x_center - 289) < cor_width or abs(x_center - 196) < cor_width or abs(x_center - 964) < cor_width or abs(x_center - 393) < cor_width or abs(x_center - 770) < cor_width or abs(x_center - 583) < cor_width or abs(x_center - 205) < cor_width or abs(x_center - 154) < cor_width or abs(x_center - 113) < cor_width or abs(x_center - 890) < cor_width:
                                    print("邊角反射跳過")
                                    continue
                                # 檢查瑕疵是否在光帶上
                                if warn_mask[y_center][x_center] == 255:
                                    # print("on laser line")
                                    # 檢查瑕疵是否在同一位置出現(1分鐘)
                                    if not min1_defectContinue:
                                        print(camera_name + "連續片 first")
                                        min1_defectContinue.append(x_center)
                                        min1_count.append([1, 1])
                                    else:
                                        # 判斷裂點是否在相同位置(1分鐘)
                                        is_crack = False
                                        for i in range(len(min1_defectContinue)):
                                            if abs(x_center - min1_defectContinue[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min1_count[i][1] == 1:
                                                    break
                                                else:
                                                    min1_count[i][1] = 1
                                                is_crack = True
                                                min1_count[i][0] = min1_count[i][0] + 1
                                                print(camera_name + "連續片 location", i, "crack count:", min1_count[i][0])
                                                break
                                        if not is_crack:
                                            min1_defectContinue.append(x_center)
                                            min1_count.append([1, 1])
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
                                    if not min5_defectHave:
                                        print(camera_name + "非連續片 first")
                                        min5_defectHave.append(x_center)
                                        min5_count.append([1, 1])
                                    else:
                                        # 判斷裂點是否在相同位置(5分鐘)
                                        is_crack = False
                                        for i in range(len(min5_defectHave)):
                                            if abs(x_center - min5_defectHave[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min5_count[i][1] == 1:
                                                    break
                                                else:
                                                    min5_count[i][1] = 1
                                                is_crack = True
                                                min5_count[i][0] = min5_count[i][0] + 1
                                                print(camera_name + "非連續片 location", i, "crack count:", min5_count[i][0])
                                                break
                                        if not is_crack:
                                            min5_defectHave.append(x_center)
                                            min5_count.append([1, 1])
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
                                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                map_now = now
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
                                map_path = predict_path + "/" + today + '/log/' + map_now + '_point_map.jpg'
                                point_map(map_path, end_time, point_time, image.shape[1], x_center, cam_number)
                                ftp_path = "RUB_crack/point_map/" + now + '_point_map.jpg'
                                ftp_upload(map_path, ftp_path)
                                
                            plc_write(defect_sum)

                    # Stop streaming
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        cv2.destroyAllWindows()
                        cam.stopStream()
                        break
            else:
                print("Image not received in time")

    terminate()

def crack_camera4():
    global device
    global in_sensor
    global speed_sensor
    global exist_glass
    global glass_mode
    camera_name = "camera_4"
    cam_number = 4
    glass_con_count = 0  # 連續玻璃數量
    glass_count = 0  # 玻璃數量
    glass_start = False
    map_save = False
    map_now = ""
    # fps_camera = 15 #相機FPS
    # width, height = image.size
    # 裂點容許數量
    min1_crack_count = 2
    min5_crack_count = 4
    # 裂點同一位置容許寬度
    crack_width = 2
    #邊角反射容許寬度
    cor_width = 3
    # 產生警戒區域遮罩
    warn_mask = np.zeros((768, 1024), dtype=np.uint8)
    # 雷射光遮罩左上 右上 右下 左下
    roi_corners = np.array([[(0, 70), (1023, 70), (1023, 95), (0, 95)]], dtype=np.int32)
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
        with Camera(0) as cam:
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
                    # Image received
                    img = cam.getCurrentImage()
                    imshow = cv2.resize(img, (640, 480))
                    cv2.imshow(camera_name, imshow)

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
                        classes, confidences, boxes = net4.detect(image, confThreshold=0.80, nmsThreshold=0.5)
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
                                #過濾邊角反射
                                if abs(x_center - 229) < cor_width or abs(x_center - 289) < cor_width or abs(x_center - 196) < cor_width or abs(x_center - 964) < cor_width or abs(x_center - 393) < cor_width or abs(x_center - 770) < cor_width or abs(x_center - 583) < cor_width or abs(x_center - 205) < cor_width or abs(x_center - 154) < cor_width or abs(x_center - 113) < cor_width or abs(x_center - 890) < cor_width:
                                    print("邊角反射跳過")
                                    continue
                                # 檢查瑕疵是否在光帶上
                                if warn_mask[y_center][x_center] == 255:
                                    # print("on laser line")
                                    # 檢查瑕疵是否在同一位置出現(1分鐘)
                                    if not min1_defectContinue:
                                        print(camera_name + "連續片 first")
                                        min1_defectContinue.append(x_center)
                                        min1_count.append([1, 1])
                                    else:
                                        # 判斷裂點是否在相同位置(1分鐘)
                                        is_crack = False
                                        for i in range(len(min1_defectContinue)):
                                            if abs(x_center - min1_defectContinue[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min1_count[i][1] == 1:
                                                    break
                                                else:
                                                    min1_count[i][1] = 1
                                                is_crack = True
                                                min1_count[i][0] = min1_count[i][0] + 1
                                                print(camera_name + "連續片 location", i, "crack count:", min1_count[i][0])
                                                break
                                        if not is_crack:
                                            min1_defectContinue.append(x_center)
                                            min1_count.append([1, 1])
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
                                    if not min5_defectHave:
                                        print(camera_name + "非連續片 first")
                                        min5_defectHave.append(x_center)
                                        min5_count.append([1, 1])
                                    else:
                                        # 判斷裂點是否在相同位置(5分鐘)
                                        is_crack = False
                                        for i in range(len(min5_defectHave)):
                                            if abs(x_center - min5_defectHave[i]) < crack_width:
                                                # 判斷是否在同一片上出現裂點
                                                if min5_count[i][1] == 1:
                                                    break
                                                else:
                                                    min5_count[i][1] = 1
                                                is_crack = True
                                                min5_count[i][0] = min5_count[i][0] + 1
                                                print(camera_name + "非連續片 location", i, "crack count:", min5_count[i][0])
                                                break
                                        if not is_crack:
                                            min5_defectHave.append(x_center)
                                            min5_count.append([1, 1])
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
                                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                map_now = now
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
                                map_path = predict_path + "/" + today + '/log/' + map_now + '_point_map.jpg'
                                point_map(map_path, end_time, point_time, image.shape[1], x_center, cam_number)
                                ftp_path = "RUB_crack/point_map/" + now + '_point_map.jpg'
                                ftp_upload(map_path, ftp_path)
                                
                            plc_write(defect_sum)

                    # Stop streaming
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        cv2.destroyAllWindows()
                        cam.stopStream()
                        break
            else:
                print("Image not received in time")

    terminate()

PLC = threading.Thread(target = PLC_RUN)
cam1 = threading.Thread(target = crack_camera1)
cam2 = threading.Thread(target = crack_camera2)
cam3 = threading.Thread(target = crack_camera3)
cam4 = threading.Thread(target = crack_camera4)

cam1.start()
cam2.start()
cam3.start()
cam4.start()
PLC.start()

