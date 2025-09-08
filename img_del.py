#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/4/23 14:47 
@Author  : 
@File    : img_del.py
@ProjectName: CRM 
'''
import pytesseract
import numpy as np
import cv2


def verification_Code(path):
    """
    :param image:
    :return:
    """
    print('开始识别验证码')
    def canny(image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        canny = cv2.Canny(blur, 50, 150)  # sick
        return canny

    print('开始识别验证码------')
    sourceimage = cv2.imread(path)
    img = np.copy(sourceimage)
    canny = canny(img)
    string = pytesseract.image_to_string(img, config='--psm 6')
    # string = pytesseract.image_to_string(img).strip()
    print('验证码为：', string,)
    yanzm = "".join(list(filter(str.isdigit, string)))
    print(yanzm)

    # return yanzm

verification_Code("res/verify.png")