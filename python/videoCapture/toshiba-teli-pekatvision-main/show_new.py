from teli import *
#from PekatVisionSDK import Instance as Pekat

import os
import cv2
import time
import datetime

initialize()

cameras = getNumOfCameras()
print("Number of cameras: %d" % cameras)

fps_camera = 30 #相機FPS
#width, height = image.size
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
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
        
    with Camera(0) as cam:
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
        #cam.setFloatValue("ExposureTime", 16000)
        print("Gain:", cam.getFloatValue("Gain"))
        #cam.setFloatValue("Gain", 0.0)
        
        # Start streaming
        cam.startStream()
        # Wait for image 2000ms
        w = cam.waitForImage(2000)
        if (w):            
            while(True):
                # Image received
                img = cam.getCurrentImage()
                imshow = cv2.resize(img, (1024,768))
                cv2.imshow('pict-orig', imshow)
                key = cv2.waitKey(1)
                if key == ord('s'):
                    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    cv2.imwrite('img/' + now + '.jpg', imshow)
                # Stop streaming
                elif key == ord('q'):
                    cv2.destroyAllWindows()
                    cam.stopStream()
                    break
                
        else:
            print("Image not received in time")

terminate()
