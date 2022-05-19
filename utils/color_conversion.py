# -*- coding:utf-8 -*-

import cv2
import numpy as np
import math
from matplotlib import pyplot as plt
from PIL import Image

# 显示图片
def cv_show(name, img):
    cv2.imshow(name, img)
    cv2.waitKey()
    cv2.destroyAllWindows()


# plt显示彩色图片
def plt_show0(img):
    b, g, r = cv2.split(img)
    img = cv2.merge([r, g, b])
    plt.imshow(img)
    plt.show()


# plt显示灰度图片
def plt_show(img):
    plt.imshow(img, cmap='gray')
    plt.show()


def conversion(color, newimg):
    resultimg = newimg.copy()
    img_gray = cv2.cvtColor(newimg, cv2.COLOR_BGR2GRAY)
    img_thre = img_gray
    th2 = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
                                cv2.THRESH_BINARY, 7, 7)
    white_num_row = []
    interval = []
    for i in range(th2.shape[0]):
        white_num = 0
        for j in range(th2.shape[1]):
            if (th2[i][j] == 0):
                th2[i][j] = 255
                white_num += 1
            else:
                th2[i][j] = 0
        white_num_row.append(white_num)
    #plt_show(th2)

    white_num_rank = []
    intervalrank = []
    for i in range(th2.shape[1]):
        white_num = 0
        for j in range(th2.shape[0]):
            if (th2[j][i] == 255):
                white_num += 1
        white_num_rank.append(white_num)

    for i in range(th2.shape[0]):
        interval.append(i)
    for i in range(th2.shape[1]):
        intervalrank.append(i)
    # bar(left, height, width, color, align, yerr)函数：绘制柱形图。
    # left为x轴的位置序列，一般采用arange函数产生一个序列；
    # height为y轴的数值序列，也就是柱形图的高度，一般就是我们需要展示的数据；
    # width为柱形图的宽度，一般这是为1即可；color为柱形图填充的颜色;
    # align设置plt.xticks()函数中的标签的位置；yerr让柱形图的顶端空出一部分。

    plt.bar(interval, white_num_row, width=1, align="edge")
    # x轴的刻度缺失一个，用上个刻度的值加上间隔补上最后的刻度
    #plt.show()
    plt.bar(intervalrank, white_num_rank, width=1, align="edge")
    # x轴的刻度缺失一个，用上个刻度的值加上间隔补上最后的刻度
    #plt.show()

    top = 0
    bottom = 80
    i = 40
    while (i < 80):
        if (white_num_row[i] < 25):
            if (i + 3 < 80):
                bottom = i + 3
            else:
                bottom = 80
            break
        i += 1

    i = 40
    while (i > 0):
        if (white_num_row[i] < 25):
            if (i - 3 >= 0):
                top = i - 3
            else:
                top = 0
            break
        i -= 1
    th2 = th2[top:bottom, 0:240]
    resultimg = resultimg[top:bottom, 0:240]
    #plt_show(th2)

    white_num_rank = []
    for i in range(th2.shape[1]):
        white_num = 0
        for j in range(th2.shape[0]):
            if (th2[j][i] == 255):
                white_num += 1
        white_num_rank.append(white_num)

    plt.bar(intervalrank, white_num_rank, width=1, align="edge")
    # x轴的刻度缺失一个，用上个刻度的值加上间隔补上最后的刻度
    #plt.show()

    left = 0
    right = 240
    i = 0
    while (i < 10):
        if (white_num_rank[i] > th2.shape[0] * 0.85):
            left = i
        i += 1

    i = 239
    while (i > 230):
        if (white_num_rank[i] > th2.shape[0] * 0.9):
            right = i
        i -= 1

    th2 = th2[0:th2.shape[0], left:right]
    resultimg = resultimg[0:th2.shape[0], left:right]
    #plt_show(th2)

    for i in range(th2.shape[0]):
        for j in range(th2.shape[1]):
            if (th2[i][j] == 0):
                resultimg[i][j][0] = 205
                resultimg[i][j][1] = 0
                resultimg[i][j][2] = 0
            else:
                resultimg[i][j][0] = 255
                resultimg[i][j][1] = 255
                resultimg[i][j][2] = 255

    #plt_show0(resultimg)
    return resultimg


def judgeColor(newimg):
    green = yello = blue = black = white = 0
    card_img_hsv = cv2.cvtColor(newimg, cv2.COLOR_BGR2HSV)
    row_num, col_num = card_img_hsv.shape[:2]
    card_img_count = row_num * col_num
    color = "no"

    for i in range(row_num):
        for j in range(col_num):
            H = card_img_hsv.item(i, j, 0)
            S = card_img_hsv.item(i, j, 1)
            V = card_img_hsv.item(i, j, 2)
            if 11 < H <= 34 and S > 34:  # 图片分辨率调整
                yello += 1
            elif 35 < H <= 99 and S > 34:  # 图片分辨率调整
                green += 1
            elif 99 < H <= 124 and S > 34:  # 图片分辨率调整
                blue += 1
    if yello * 2 >= card_img_count:
        color = "yellow"
    elif green * 2 >= card_img_count:
        color = "green"
    elif blue * 2 >= card_img_count:
        color = "blue"

    return color


# def dealgreen(th2, rawImage):
#     rawImage2 = rawImage.copy()
#     th3 = th2.copy()
#     th4 = th2.copy()
#     intervalrank = []
#     white_num_rank = []
#     for i in range(th2.shape[1]):
#         intervalrank.append(i)
#
#     for i in range(th2.shape[1]):
#         white_num = 0
#         for j in range(th2.shape[0]):
#             if (th2[j][i] == 255):
#                 white_num += 1
#         white_num_rank.append(white_num)
#
#     plt.bar(intervalrank, white_num_rank, width=1, align="edge")
#     # x轴的刻度缺失一个，用上个刻度的值加上间隔补上最后的刻度
#     plt.show()
#
#     leftlimit = 100
#     rightlimit = 100
#     leftlocation = 190
#     rightlocation = 220
#     for i in range(200,230):
#         if white_num_rank[i] < 0.08 * th2.shape[0] and white_num_rank[i] < rightlimit:
#             rightlimit = white_num_rank[i]
#             rightlocation = i
#     for i in range(170,200):
#         if white_num_rank[i] < 0.08 * th2.shape[0] and white_num_rank[i] < leftlimit:
#             leftlimit = white_num_rank[i]
#             leftlocation = i
#
#     th3 = th3[0:th3.shape[0], 0:rightlocation]
#     plt_show(th3)
#     for i in range(leftlocation, leftlocation+th4.shape[1]-rightlocation):
#         for j in range(0,th4.shape[0]):
#             th4[j][i] = th4[j][rightlocation+i-leftlocation]
#     th4 = th4[0:th4.shape[0], 0:leftlocation+th4.shape[1]-rightlocation-1]
#     plt_show(th4)
#
#     rawImage = rawImage[0:th3.shape[0],0:th3.shape[1]]
#     for i in range(th3.shape[0]):
#         for j in range(th3.shape[1]):
#             if (th3[i][j] == 0):
#                 rawImage[i][j][0] = 205
#                 rawImage[i][j][1] = 0
#                 rawImage[i][j][2] = 0
#             else:
#                 rawImage[i][j][0] = 255
#                 rawImage[i][j][1] = 255
#                 rawImage[i][j][2] = 255
#
#     rawImage2 = rawImage2[0:th4.shape[0],0:th4.shape[1]]
#     for i in range(th4.shape[0]):
#         for j in range(th4.shape[1]):
#             if (th4[i][j] == 0):
#                 rawImage2[i][j][0] = 205
#                 rawImage2[i][j][1] = 0
#                 rawImage2[i][j][2] = 0
#             else:
#                 rawImage2[i][j][0] = 255
#                 rawImage2[i][j][1] = 255
#                 rawImage2[i][j][2] = 255
#
#     return rawImage, rawImage2

# def dealgreen(img):
#     Lic_img = []
#     left = [20, 45, 65, 85, 110 ,140, 170, 200]
#     right =[40, 65, 85,110, 140, 170, 200, 230]
#     intervalrank = []
#     white_num_rank = []
#     last = 0
#     for i in range(img.shape[1]):
#         intervalrank.append(i)
#
#     for i in range(img.shape[1]):
#         white_num = 0
#         for j in range(img.shape[0]):
#             if (img[j][i] == 255):
#                 white_num += 1
#         white_num_rank.append(white_num)
#     for i in range(8):
#         height = 100
#         min = left[i]
#         max = right[i]
#         middle = 0
#         for j in range(min, max):
#             if white_num_rank[j] < 0.08 * img.shape[0] and white_num_rank[j] < height:
#                 middle = j
#                 height = white_num_rank[j]
#         if i != 2:
#             Lic_img.append(img[0:img.shape[0], last:middle])
#         last = middle
#
#     middle = img.shape[1]
#     Lic_img.append(img[0:img.shape[0], last:middle])
#     return Lic_img


def dealgreen(rawImage):
    #img = cv2.imread("F:\\Final_LPR_Model\\plate_model\\greencar.png")
    #plt_show0(img)
    #img = cv2.resize(img, (260, 80), interpolation=cv2.INTER_AREA)
    imgcopy = rawImage.copy()
    # imgcopy = cv2.resize(imgcopy, (260, 80), interpolation=cv2.INTER_AREA)
    # for i in range(260):
    #     for j in range(80):
    #         if i < 10:
    #             imgcopy[j][i][0] = rawImage[j][0][0]
    #             imgcopy[j][i][1] = rawImage[j][0][1]
    #             imgcopy[j][i][2] = rawImage[j][0][2]
    #         elif i >= 250:
    #             imgcopy[j][i][0] = rawImage[j][239][0]
    #             imgcopy[j][i][1] = rawImage[j][239][1]
    #             imgcopy[j][i][2] = rawImage[j][239][2]
    #         else:
    #             imgcopy[j][i][0] = rawImage[j][i-10][0]
    #             imgcopy[j][i][1] = rawImage[j][i-10][1]
    #             imgcopy[j][i][2] = rawImage[j][i-10][2]
    # imgcopy = cv2.resize(imgcopy, (240, 80), interpolation=cv2.INTER_AREA)
    imgcopy = cv2.copyMakeBorder(imgcopy, 0, 0, 4, 4, cv2.BORDER_REFLECT)
    # imgcopy = cv2.copyMakeBorder(imgcopy, 0, 0, 4, 4, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    imgcopy = cv2.resize(imgcopy, (240, 80), interpolation=cv2.INTER_AREA)
    return imgcopy


def colorConversion(Lic_img):
    Lic_img_return = []
    for i in range(len(Lic_img)):
        rawImage = cv2.resize(Lic_img[i], (240, 80), interpolation=cv2.INTER_AREA)
        colorresult = judgeColor(rawImage)
        if colorresult == "blue":
            Lic_img_return.append(rawImage)
        elif colorresult == "yellow":
            #img = conversion(colorresult, rawImage)
            #img = cv2.resize(img, (240, 80), interpolation=cv2.INTER_AREA)
            Lic_img_return.append(rawImage)
        elif colorresult == "green":
            # plt_show0(rawImage)
            # rawImage = dealgreen(rawImage)
            # plt_show0(rawImage)
            Lic_img_return.append(rawImage)

            # img, imgcopy = dealgreen(img, rawImage)
            # img = cv2.resize(img, (240, 80), interpolation=cv2.INTER_AREA)
            # imgcopy = cv2.resize(imgcopy, (240, 80), interpolation=cv2.INTER_AREA)
            # plt_show0(img)
            # plt_show0(imgcopy)
            # Lic_img_return.append(img)
            # Lic_img_return_copy.append(imgcopy)
        else:
            continue

    return colorresult, Lic_img_return
