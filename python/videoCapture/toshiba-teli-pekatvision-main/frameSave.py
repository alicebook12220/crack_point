#video to frame
import cv2
vc = cv2.VideoCapture("test.avi")
fps = vc.get(cv2.CAP_PROP_FPS)
print("video fps:",fps)
frame_count = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
print("frame count:",frame_count)
video = []
count = 0

for idx in range(frame_count):
    if idx % 100 == 0:
        print("processing " + str(idx) + " images")
    count = count + 1
    vc.set(1, idx)
    ret, frame = vc.read()
    
    if frame is not None:
        #---演算法寫這----
        cv2.imwrite('frame/frame_' + str(count) + '.jpg', frame)
        #new_frame = f(frame)
        #---------------
        #height, width, layers = new_frame.shape
        #size = (width, height)
        #video.append(new_frame)

vc.release()