from teli import *
import cv2
import numpy as np
import time
import datetime
import glob
import os
import ftplib
import csv

host = "192.168.3.100"
username = "ftpuser"
password = "ftp@12345678"
camera_name = "camera_1"
station_name = "RUB_crack"
predict_path = "C:/Users/user/Desktop/" + station_name

def ftp_upload(file_path, ftp_path):
    ftp_session = ftplib.FTP(host)
    ftp_session.login(username, password)
    file = open(file_path, 'rb')
    ftp_session.storbinary('STOR ' + ftp_path, file)
    file.close()
    ftp_session.quit()

def csv_write(mode="header", today="test", result=0):
    print("csv mode:", mode)
    data = ""
    if mode == "header":
        data = ['datetime', 'result']
    else:
        now = datetime.datetime.now().strftime("%Y%m%d %H%M%S")
        data = [now, result]

    with open(predict_path + "/" + today + '/log/' + today + "_" + camera_name + '_result.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the data
        writer.writerow(data)

net = cv2.dnn_DetectionModel('C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/cfg/custom-yolov4-3l-tiny.cfg', 'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/backup/custom-yolov4-tiny_last.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net.setInputSize(1024, 768)
net.setInputScale(1.0 / 255)
net.setInputSwapRB(True) 

initialize()

cameras = getNumOfCameras()
print("Number of cameras: %d" % cameras)

#fps_camera = 15 #相機FPS
#width, height = image.size
#裂點容許數量
min1_crack_count = 2
min5_crack_count = 4
#裂點同一位置容許寬度
crack_width = 2
#產生警戒區域遮罩
warn_mask = np.zeros((768, 1024), dtype=np.uint8)
#雷射光遮罩左上 右上 右下 左下
roi_corners = np.array([[(0, 360), (1023, 360), (1023, 415), (0, 415)]], dtype=np.int32)
channel_count = 1
ignore_mask_color = (255,)*channel_count
cv2.fillPoly(warn_mask, roi_corners, ignore_mask_color)

#time_temp = str(datetime.date.today())
if (cameras):
    # At least one camera
    for i in range(cameras):
        info = getCameraInfo(i)
        print("Camera %d" % i)
        print("  Camera type: %s" % info.camType)
        print("  Manufacturer: %s" % info.manufacturer)
        print("  Model: %s" % info.modelName)
        print("  Serial no: %s" % info.serialNumber)
        print("  User name: %s" % info.userDefinedName)
        
    # Connect to Pekat
    #pekat = Pekat(host = "127.0.0.1", port = 8100, already_running = True)
    with Camera(0) as cam:
        # How to get and set properties
        # String
        # print(cam.getStringValue("DeviceUserID"))
        # cam.setStringValue("DeviceUserID", "My camera")
        # Enum 圖像模式
        #print(cam.getEnumStringValue("TestPattern"))
        #cam.setEnumStringValue("TestPattern", "Off")
        # Int 偵數
        print("Frame Count:",cam.getIntValue("AcquisitionFrameCount"))
        #cam.setIntValue("AcquisitionFrameCount", fps_camera)
        # Float 曝光時間
        print("Exposure Time:", cam.getFloatValue("ExposureTime"))
        #cam.setFloatValue("ExposureTime", 5000)
        print("Gain:", cam.getFloatValue("Gain"))
        #cam.setFloatValue("Gain", 24.0)
        
        OK_img_count = 1
        NG_img_count = 1
        # Start streaming
        cam.startStream()
        # Wait for image 2000ms
        w = cam.waitForImage(2000)
        time_OK = time.time()
        csv_time = time.time()
        if (w):
            min1_defectContinue = []
            min5_defectHave = []
            min1_count = []
            min5_count = []
            start_min1 = time.time()
            start_min5 = time.time()
            find_crack_t1 = 0
            find_crack_t5 = 0
            while(True):
                today = str(datetime.date.today())
                '''
                if time_temp != time_now:
                    time_temp = time_now
                    OK_img_count = 1
                    NG_img_count = 1
                '''
                # Image received
                img = cam.getCurrentImage()
                imshow = cv2.resize(img, (1024,768))
                cv2.imshow('Realtime Show Cam1', imshow)
                
                output_path = predict_path + "/" + today
                isExists = os.path.exists(output_path)
                if not isExists:
                    #print("建立日期目錄:", today)
                    #os.makedirs(output_path)
                    os.makedirs(output_path + "/OK/")
                    #os.makedirs(output_path + "NG/")
                    os.makedirs(output_path + "/NG/box")
                    os.makedirs(output_path + "/NG/nobox")
                    os.makedirs(output_path + '/log')
                isExists = os.path.exists(predict_path + "/" + today + '/log/' + today + "_" + camera_name + '_result.csv')
                if not isExists:
                    csv_write("header", today)
                #predict
                image = cv2.resize(img, (1024,768))
                image_nobox = image.copy()
                image_light = image[warn_mask == 255]
                image_light = np.mean(image_light)
                if time.time() - csv_time > 14400: #14400
                    csv_time = time.time()
                    csv_write("OK", today, 0)
                    csv_path = predict_path + "/" + today + '/log/' + today + "_" + camera_name + '_result.csv'
                    try:
                        ftp_path = "RUB_crack/log/" + today + "_" + camera_name + ".csv"
                        ''''
                        isExists = os.path.exists(output_path)
                        if not isExists:
                            #print("建立日期目錄:", today)
                            #os.makedirs(output_path)
                            os.makedirs(output_path + "/OK/")
                        '''
                        ftp_upload(csv_path, ftp_path)
                    except:
                        print("ftp server connect error")
                        pass
                print("image_light:",image_light)
                if image_light > 1 and image_light < 20:
                    start = time.time()
                    classes, confidences, boxes = net.detect(image, confThreshold=0.85, nmsThreshold=0.5)
                    #print(time.time()-start)
                    alarm_status = False
                    if len(boxes) > 0:
                        for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
                            pstring = str(int(100 * confidence)) + "%"
                            x_left, y_top, width, height = box
                            
                            boundingBox = [
                                (x_left, y_top), #左上頂點
                                (x_left, y_top + height), #左下頂點
                                (x_left + width, y_top + height), #右下頂點
                                (x_left + width, y_top) #右上頂點
                            ]
                            rectColor = (0, 0, 255)
                            textCoord = (x_left, y_top - 10)
                            #在影像中標出Box邊界和類別、信心度
                            cv2.rectangle(image, boundingBox[0], boundingBox[2], rectColor, 2)
                            cv2.putText(image, pstring, textCoord, cv2.FONT_HERSHEY_DUPLEX, 1, rectColor, 2)
                            
                            x_center = x_left + int(width/2)
                            y_center = y_top + int(height/2)
                            #檢查瑕疵是否在光帶上
                            if warn_mask[y_center][x_center] == 255:
                                #print("on laser line")
                                #檢查瑕疵是否在同一位置出現(1分鐘)
                                if not min1_defectContinue:
                                    print("min1 first")
                                    find_crack_t1 = time.time()
                                    min1_defectContinue.append(x_center)
                                    min1_count.append(1)
                                else:
                                    #判斷裂點是否在相同位置(1分鐘)
                                    is_crack = False
                                    for i in range(len(min1_defectContinue)):
                                        if abs(x_center - min1_defectContinue[i]) < crack_width:
                                            is_crack = True
                                            #是否在同一片上出現裂點
                                            if time.time() - find_crack_t1 < 10:
                                                break
                                            find_crack_t1 = time.time()
                                            min1_count[i] = min1_count[i] + 1
                                            print("min1 location", i,"crack count:", min1_count[i])
                                            break
                                    if not is_crack:
                                        min1_defectContinue.append(x_center)
                                        min1_count.append(1)
                                #判斷相同位置裂點是否大於2個(1分鐘)
                                if time.time() - start_min1 < 60:
                                    defect_sum = sum(i > min1_crack_count for i in min1_count)
                                    if defect_sum > 0: 
                                        #發報
                                        alarm_status = True
                                        start_min1 = time.time()
                                        start_min5 = time.time()
                                        min1_defectContinue.clear()
                                        min5_defectHave.clear()
                                        min1_count.clear()
                                        min5_count.clear()
                                        print("min1 Alarm")
                                        break
                                else:
                                    start_min1 = time.time()
                                    min1_defectContinue.clear()
                                    min1_count.clear()
                                
                                if not min5_defectHave:
                                    print("min5 first")
                                    find_crack_t5 = time.time()
                                    min5_defectHave.append(x_center)
                                    min5_count.append(1)
                                else:
                                    #判斷裂點是否在相同位置(5分鐘)
                                    is_crack = False
                                    for i in range(len(min5_defectHave)):
                                        if abs(x_center - min5_defectHave[i]) < crack_width:
                                            is_crack = True
                                            #是否在同一片上出現裂點
                                            if time.time() - find_crack_t5 < 10:
                                                break
                                            find_crack_t5 = time.time()
                                            min5_count[i] = min5_count[i] + 1
                                            print("min5 location", i,"crack count:", min5_count[i])
                                            break
                                    if not is_crack:
                                        min5_defectHave.append(x_center)
                                        min5_count.append(1)
                                #判斷相同位置裂點是否大於4個(5分鐘)
                                if time.time() - start_min5 < 300:
                                    defect_sum = sum(i > min5_crack_count for i in min5_count)
                                    if defect_sum > 0: 
                                        #發報
                                        alarm_status = True
                                        start_min1 = time.time()
                                        start_min5 = time.time()
                                        min1_defectContinue.clear()
                                        min5_defectHave.clear()
                                        min1_count.clear()
                                        min5_count.clear()
                                        print("min5 Alarm")
                                        break
                                elif time.time() - start_min5 > 300:
                                    start_min5 = time.time()
                                    min5_defectHave.clear()
                                    min5_count.clear()
                        #如果Alarm，存圖並上傳到FTP Server
                        if alarm_status:
                            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            csv_write("NG", today, 1)
                            csv_path = predict_path + "/" + today + '/log/' + today + "_" + camera_name + '_result.csv'
                            alarm_status = False
                            img_box_path = output_path + "/NG/box/" + now + ".jpg"
                            img_nobox_path = output_path + "/NG/nobox/" + now + ".jpg"
                            cv2.imwrite(img_box_path, image)
                            cv2.imwrite(img_nobox_path, image_nobox)
                            #NG_img_count = NG_img_count + 1
                            cv2.imshow('crack_cam1', image)
                            try:
                                ftp_path = "RUB_crack/box/" + now + ".jpg" 
                                ftp_upload(img_box_path, ftp_path)
                                ftp_path = "RUB_crack/nobox/" + now + ".jpg" 
                                ftp_upload(img_nobox_path, ftp_path)
                                ftp_path = "RUB_crack/log/" + today + "_" + camera_name + ".csv"
                                ftp_upload(csv_path, ftp_path)
                            except:
                                print("ftp server connect error")
                                pass
                    else:
                        if time.time() - time_OK > 16:
                            time_OK = time.time()
                            #cv2.imshow('crack', image)
                            output_path = predict_path + "/" + today
                            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            cv2.imwrite(output_path + "/OK/" + now + ".jpg", image)
                
                '''
                date_s_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                date_h_time = datetime.datetime.now().strftime("%Y-%m-%d_%H")
                date_d_time = datetime.datetime.now().strftime("%Y-%m-%d")
                #print(date_s_time)
                #print(date_h_time)
                #print(date_m_time)
                output_path = "log/" + str(date_d_time)
                isExists = os.path.exists(output_path)
                if not isExists:
                    print("建立log日期目錄:", date_d_time)
                    os.makedirs(output_path)
                # 開啟檔案
                fp = open(output_path + "/" + date_h_time + ".txt", "a")
                if crack_status:
                    # 寫入檔案
                    fp.write(date_s_time + " 1" + "\n")
                else:
                    if OK_img_count > 100:
                        fp.write(date_s_time + " 0" + "\n")
                # 關閉檔案
                fp.close()
                '''
                # Stop streaming
                key = cv2.waitKey(1)
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    cam.stopStream()
                    break     
        else:
            print("Image not received in time")

terminate()
