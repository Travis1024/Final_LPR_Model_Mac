# -*- coding:utf-8 -*-
import os.path
import sys
# from tkinter import *
# from tkinter.filedialog import askopenfilename
from PIL import ImageTk
from tensorflow import keras
from utils.locate_and_correct import *
from utils.color_conversion import *
from unet import *
from cnn_utils.cnn import *
from cnn_utils.cnngreen import *
from cnn_utils.cnnyellow import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from dbHandle import *


class MyDirEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.window = Window()

    def on_created(self, event):
        print(event)
        listevent = event.src_path.split('/')
        orgid = listevent[len(listevent)-2]
        # print(orgid)
        fileName = str(event.src_path.split('/')[-1])
        # print(fileName)
        if fileName != ".DS_Store":
            if orgid.find('_') == -1:
                self.window.predict_func(fileName, orgid)
            else:
                self.window.predict_func_leave(fileName, orgid)

class Window:
    def __init__(self):
        self.img_dir = "/Users/travis/UniversityFiles/GraduationFiles/plateDataDir"
        self.net_img_dir = "http://localhost:8089/imgdir"
        self.unet = keras.models.load_model('model/unetnew.h5')
        self.cnn = keras.models.load_model('model/cnnblue57.h5')
        self.cnngreen = keras.models.load_model('model/cnngreen317.h5')
        self.cnnyellow = keras.models.load_model('model/cnnyellow326.h5')
        print('正在启动中,请稍等...')
        cnn_predict(self.cnn, [np.zeros((80, 240, 3))])
        cnn_predict_green(self.cnngreen, [np.zeros((80, 240, 3))])
        cnn_predict_yellow(self.cnnyellow, [np.zeros((80, 240, 3))])
        print("已启动,开始识别！")

    def predict_func(self, img_name, orgid):
        # 从中文路径读取时用
        img_name = os.path.join(orgid, img_name)
        img_src_path = os.path.join(self.img_dir, img_name)
        print(img_src_path)
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

        platecolor, Lic_img = colorConversion(Lic_img)
        if platecolor == "blue" or platecolor == "yellow" or platecolor == "green":
            if platecolor == "blue":
                Lic_pred = cnn_predict(self.cnn, Lic_img)
            elif platecolor == "yellow":
                Lic_pred = cnn_predict_yellow(self.cnnyellow, Lic_img)
            elif platecolor == "green":
                Lic_pred = cnn_predict_green(self.cnngreen, Lic_img)

            if Lic_pred:
                # img_src_copy[:, :, ::-1]将BGR转为RGB
                # img = Image.fromarray(img_src_copy[:, :, ::-1])

                for i, lic_pred in enumerate(Lic_pred):
                    if i == 0:
                        net_img_path = os.path.join(self.net_img_dir, img_name)
                        # print(net_img_path)
                        # print(orgid)
                        # print(platecolor)
                        # print(lic_pred[1])
                        handleAddCar(net_img_path, lic_pred[1], platecolor, orgid)
                        print("======成功进入！======")

            # Lic_pred为空说明未能识别
            else:
                print("未能识别成功！")
        else:
            print("车牌识别失败！")

    def predict_func_leave(self, img_name, orgid):
        # 从中文路径读取时用
        img_name = os.path.join(orgid, img_name)
        img_src_path = os.path.join(self.img_dir, img_name)
        print(img_src_path)
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

        platecolor, Lic_img = colorConversion(Lic_img)
        if platecolor == "blue" or platecolor == "yellow" or platecolor == "green":
            if platecolor == "blue":
                Lic_pred = cnn_predict(self.cnn, Lic_img)
            elif platecolor == "yellow":
                Lic_pred = cnn_predict_yellow(self.cnnyellow, Lic_img)
            elif platecolor == "green":
                Lic_pred = cnn_predict_green(self.cnngreen, Lic_img)

            if Lic_pred:
                # img_src_copy[:, :, ::-1]将BGR转为RGB
                # img = Image.fromarray(img_src_copy[:, :, ::-1])

                for i, lic_pred in enumerate(Lic_pred):
                    if i == 0:
                        net_img_path = os.path.join(self.net_img_dir, img_name)
                        # print(net_img_path)
                        # print(orgid)
                        # print(platecolor)
                        # print(lic_pred[1])
                        if handleCarLeave(net_img_path, lic_pred[1], platecolor, orgid):
                            print("======成功离开！======")
                        else:
                            print("======异常错误，请联系值班人员手动处理！======")

            # Lic_pred为空说明未能识别
            else:
                print("未能识别成功！")
        else:
            print("车牌识别失败！")

    def clear(self):
        self.img_dir = None


if __name__ == '__main__':
    observer = Observer()
    fileHandler = MyDirEventHandler()
    observer.schedule(fileHandler, "/Users/travis/UniversityFiles/GraduationFiles/plateDataDir", True)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
