from teli import *
import cv2
import numpy as np
import time
import datetime
import glob
import os

net = cv2.dnn_DetectionModel('C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/cfg/custom-yolov4-3l-tiny.cfg', 'C:/Users/user/Desktop/crack_point/python/videoCapture/toshiba-teli-pekatvision-main/backup/custom-yolov4-tiny_last.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
net.setInputSize(1024, 768)
net.setInputScale(1.0 / 255)
net.setInputSwapRB(True) 

initialize()

cameras = getNumOfCameras()
print("Number of cameras: %d" % cameras)

fps_camera = 15 #相機FPS
predict_path = "C:/Users/user/Desktop/RUB_img/"
#width, height = image.size

crack_status = False
time_temp = str(datetime.date.today())

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
        cam.setIntValue("AcquisitionFrameCount", fps_camera)
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
        if (w):            
            while(True):
                time_now = str(datetime.date.today())
                if time_temp != time_now:
                    time_temp = time_now
                    OK_img_count = 1
                    NG_img_count = 1
                # Image received
                img = cam.getCurrentImage()
                imshow = cv2.resize(img, (480,320))
                cv2.imshow('pict-orig', imshow)
                
                output_path = predict_path + str(time_now)
                isExists = os.path.exists(output_path)
                if not isExists:
                    print("建立日期目錄:", time_now)
                    #os.makedirs(output_path)
                    os.makedirs(output_path + "/OK/")
                    #os.makedirs(output_path + "NG/")
                    os.makedirs(output_path + "/NG/box")
                    os.makedirs(output_path + "/NG/nobox")
                
                #predict
                image = cv2.resize(img, (1024,768))
                image_nobox = image.copy()
                start = time.time()
                classes, confidences, boxes = net.detect(image, confThreshold=0.85, nmsThreshold=0.5)
                #print(time.time()-start)
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
                        
                        if int(100 * confidence) > 1:
                        # 在影像中標出Box邊界和類別、信心度
                            cv2.rectangle(image, boundingBox[0], boundingBox[2], rectColor, 2)
                            cv2.putText(image, pstring, textCoord, cv2.FONT_HERSHEY_DUPLEX, 1, rectColor, 2)
                        crack_status = True
                    if crack_status:
                        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        cv2.imwrite(output_path + "/NG/box/" + now + ".jpg", image)
                        cv2.imwrite(output_path + "/NG/nobox/" + now + ".jpg", image_nobox)
                        NG_img_count = NG_img_count + 1
                        cv2.imshow('crack', image)
                else:
                    crack_status = False
                    if time.time() - time_OK > 8:
                        time_OK = time.time()
                        #cv2.imshow('crack', image)
                        output_path = predict_path + str(time_now)
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
