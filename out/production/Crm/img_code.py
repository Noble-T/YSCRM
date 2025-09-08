#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/4/23 13:55 
@Author  : 
@File    : img_code.py
@ProjectName: CRM 
'''

import cv2
import pytesseract


def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 调整对比度和亮度（可选）
    img = cv2.convertScaleAbs(img, alpha=0.5, beta=50)

    # 二值化
    _, img = cv2.threshold(img, 0, 250, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU) # 使用OTSU算法进行二值化

    # 中值滤波（可选，去除椒盐噪声）
    img = cv2.medianBlur(img, 5)
    # 显示处理后的图像
    cv2.imwrite('res/preprocessed_captcha.png', img)

    return img


def recognize_captcha(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    result = pytesseract.image_to_string(img, lang='eng', config='--psm 7')  # 设置单行文本模式
    return result.strip()  # 移除多余空格


if __name__ == "__main__":
    original_image_path = "res/verify.png"
    preprocessed_image_path = "res/preprocessed_captcha.png"

    preprocessed_img = preprocess_image(original_image_path)
    cv2.imwrite(preprocessed_image_path, preprocessed_img)

    captcha_text = recognize_captcha(preprocessed_image_path)
    print(f"Captcha text: {captcha_text}")