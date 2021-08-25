from teli import *
#from PekatVisionSDK import Instance as Pekat

import os
import cv2
import time
import datetime

initialize()

cameras = getNumOfCameras()
print("Number of cameras: %d" % cameras)

fps_camera = 10 #相機FPS
#width, height = image.size
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_status = True

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
        cam.setFloatValue("ExposureTime", 5000)
        print("Gain:", cam.getFloatValue("Gain"))
        cam.setFloatValue("Gain", 24.0)
        
        # Start streaming
        cam.startStream()
        # Wait for image 2000ms
        w = cam.waitForImage(2000)
        if (w):
            time_now = datetime.date.today()
            output_path = "video/" + str(time_now) + "_1/"
            isExists = os.path.exists(output_path)
            if not isExists:
                print("建立日期目錄:", time_now)
                os.makedirs(output_path)
            else:
                count = 2
                while(True):
                    output_path = "video/" + str(time_now) + "_" + str(count) + "/"
                    isExists = os.path.exists(output_path)
                    if not isExists:
                        print("建立日期目錄", time_now)
                        os.makedirs(output_path)
                        break
                    else:
                        count = count + 1
                        
            video_Start = time.time()
            video_count = 1
            img_count = 1
            output_img_path = output_path + str(video_count) + "/"
            isExists = os.path.exists(output_img_path)
            if not isExists:
                print("建立影像目錄:", video_count)
                os.makedirs(output_img_path)
            #video = cv2.VideoWriter(output_path + str(video_count) + '.avi', fourcc, fps_video, (1024, 768))
            while(True):
                # Image received
                img = cam.getCurrentImage()
                img = cv2.resize(img, (1024,768))
                cv2.imshow('pict-orig.png', img)
                
                #cv2.imwrite('pict-annotated.png', img_res)
                if video_status:
                    #video.write(img)
                    cv2.imwrite(output_img_path + str(img_count) + ".jpg", img)
                    img_count = img_count + 1
                    video_End = time.time()
                    video_time = video_End - video_Start
                    if video_time > 23:
                        #video.release()
                        video_count = video_count + 1
                        img_count = 1
                        output_img_path = output_path + str(video_count) + "/"
                        isExists = os.path.exists(output_img_path)
                        if not isExists:
                            print("建立影像目錄:", video_count)
                            os.makedirs(output_img_path)
                        #video = cv2.VideoWriter(output_path + str(video_count) + '.avi', fourcc, fps_video, (1024, 768))
                        video_Start = time.time()
                        #wait_Start = time.time()
                        #video_status = False
                '''
                else:
                    wait_End = time.time()
                    wait_time = wait_End - wait_Start
                    if wait_time > 30:
                        video_count = video_count + 1
                        video = cv2.VideoWriter(output_path + str(video_count) + '.avi', fourcc, fps_video, (1024, 768))
                        video_Start = time.time()
                        video_status = True
                '''
                # Stop streaming
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    video.release()
                    cv2.destroyAllWindows()
                    cam.stopStream()
                    break
        else:
            print("Image not received in time")

terminate()

'''
import cv2

# 選擇第二隻攝影機
cap = cv2.VideoCapture(2)

while(True):
  # 從攝影機擷取一張影像
  ret, frame = cap.read()

  # 顯示圖片
  cv2.imshow('frame', frame)

  # 若按下 q 鍵則離開迴圈
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# 釋放攝影機
cap.release()

# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()
'''