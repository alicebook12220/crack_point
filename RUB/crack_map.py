import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
my_font = font_manager.FontProperties(fname=r"C:\Windows\Fonts\msjhbd.ttc", size=18)

#plt.figure(figsize=(8,8))   # 顯示圖框架大小

plt.style.use("ggplot")     # 使用ggplot主題樣式
plt.xlabel("玻璃長度(以時間計算)", fontsize = 24, fontweight = "bold", fontproperties=my_font)  #設定x座標標題及粗體
plt.ylabel("玻璃寬度(以像素計算)", fontsize = 24, fontweight = "bold", fontproperties=my_font)  #設定y座標標題及粗體
plt.title("玻璃裂點位置圖", fontsize = 24, fontweight = "bold", fontproperties=my_font)        #設定標題、字大小及粗體
plt.xlim(0,1500)
plt.ylim(0,3072)

plt.scatter(210,                    # x軸資料
            500,     # y軸資料
            c = "m",                                  # 點顏色
            s = 50,                                   # 點大小
            alpha = .5,                               # 透明度
            marker = "D")                             # 點樣式

plt.savefig("Scatter of Number of cars and Number of passengers(million).jpg")   #儲存圖檔
plt.show()
plt.close()      # 關閉圖表
