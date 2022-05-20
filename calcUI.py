# -*- coding:utf-8 -*-
from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import ImageTk
from tensorflow import keras
from utils.locate_and_correct import *
from utils.color_conversion import *
from unet import *
from cnn_utils.cnn import *
from cnn_utils.cnngreen import *
from cnn_utils.cnnyellow import *
import time
import shutil


class Window:
    def __init__(self, pic_path):
        self.pic_path = pic_path
        self.unet = keras.models.load_model('model/unetnew.h5')  # 蓝黄绿
        self.cnn = keras.models.load_model('model/cnnblue57.h5')  # 暂时为蓝牌和绿牌，黄牌为颜色空间映射
        self.cnngreen = keras.models.load_model('model/cnngreen317.h5')
        self.cnnyellow = keras.models.load_model('model/cnnyellow326.h5')
        print('正在启动中,请稍等...')
        cnn_predict(self.cnn, [np.zeros((80, 240, 3))])
        cnn_predict_green(self.cnngreen, [np.zeros((80, 240, 3))])
        cnn_predict_yellow(self.cnnyellow, [np.zeros((80, 240, 3))])
        print("已启动,开始识别吧！")

    def circleFile(self):
        number = 0
        alltruenumber = 0
        for file in os.listdir(self.pic_path):
            filepath = str(file)
            print("==================" + str(number) + "==================")
            number = number + 1
            print(filepath)
            img_src_path = pic_path + filepath
            predictResult, plateColor = self.predict(img_src_path)
            # filepath2 = filepath[0:7]
            predictResult = predictResult.replace('·', '')
            print(predictResult)
            # if filepath2 == predictResult:
            #     alltruenumber += 1
            # print(alltruenumber)

        print("------------alltruenumber = " + str(alltruenumber) + "------------")

    def predict(self, img_src_path):
        # 还没选择图片就进行预测
        # 从中文路径读取时用
        img_src = cv2.imdecode(np.fromfile(img_src_path, dtype=np.uint8), -1)
        h, w = img_src.shape[0], img_src.shape[1]

        # 满足该条件说明可能整个图片就是一张车牌,无需定位,直接识别即可
        if h * w <= 240 * 80 and 2 <= w / h <= 5:
            # 直接resize为(240,80)
            lic = cv2.resize(img_src, dsize=(240, 80), interpolation=cv2.INTER_AREA)[:, :, :3]
            img_src_copy, Lic_img = img_src, [lic]

        # 否则就需通过unet对img_src原图预测,得到img_mask,实现车牌定位,然后进行识别
        else:
            img_src, img_mask = unet_predict(self.unet, img_src_path)
            # 利用core.py中的locate_and_correct函数进行车牌定位和矫正
            img_src_copy, Lic_img = locate_and_correct(img_src,
                                                       img_mask)
        try:
            platecolor, Lic_img = colorConversion(Lic_img)
        except Exception as e:
            return "NULL", "NULL"
        print(platecolor)
        if platecolor == "blue":
            Lic_pred = cnn_predict(self.cnn, Lic_img)
        elif platecolor == "yellow":
            Lic_pred = cnn_predict_yellow(self.cnnyellow, Lic_img)
        elif platecolor == "green":
            Lic_pred = cnn_predict_green(self.cnngreen, Lic_img)

        # 利用cnn进行车牌的识别预测,Lic_pred中存的是元祖(车牌图片,识别结果)
        # Lic_pred = cnn_predict(self.cnn, Lic_img)
        if platecolor != "no":
            if Lic_pred:
                for i, lic_pred in enumerate(Lic_pred):
                    if i == 0:
                        return lic_pred[1], platecolor

        # Lic_pred为空说明未能识别
        return "NULL", "NULL"


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pic_path = "/Users/travis/UniversityFiles/GraduationFiles/plate/"
    ww = Window(pic_path)
    time_start = time.time()
    ww.circleFile()
    time_end = time.time()
    timesum = time_end - time_start
    print(timesum)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
