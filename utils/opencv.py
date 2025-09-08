#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2025/3/13 15:51 
@Author  : 
@File    : opencv.py
@ProjectName: CRM

pip install pytesseract opencv-python pillow numpy

提高识别准确率的方法
1. 图像预处理
灰度化：将彩色图像转换为灰度图像。
二值化：将灰度图像转换为黑白图像，以便更容易识别字符。
去噪：去除图像中的噪声，例如使用形态学操作（如腐蚀、膨胀）。
边缘检测：使用Canny等算法检测图像边缘，有助于分离字符。
2. 调整Tesseract配置
PSM（Page Segmentation Mode）：设置适当的页面分割模式，例如--psm 10表示将图像视为单个字符。
OEM（OCR Engine Mode）：选择合适的OCR引擎模式，例如--oem 3表示使用LSTM OCR引擎。
字符白名单：限制识别的字符范围，例如-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789。
3. 训练自定义模型
如果验证码有特定的风格或干扰，可以考虑训练一个自定义的OCR模型，使用深度学习框架如TensorFlow或PyTorch。
4. 数据增强
在训练数据时，可以通过旋转、缩放、添加噪声等方式增强数据集，提高模型的泛化能力。
通过上述方法，可以有效提高验证码识别的准确率。
'''
import cv2
import numpy as np
from PIL import Image
import pytesseract

# 配置Tesseract路径（如果需要）
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    # 读取图片
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 图像二值化
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

    # 去噪
    kernel = np.ones((2, 2), np.uint8)
    denoised_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

    return denoised_image

def recognize_captcha(image_path):
    # 预处理图片
    processed_image = preprocess_image(image_path)

    # 使用PIL转换为Image对象
    img = Image.fromarray(processed_image)

    # 使用Tesseract进行OCR识别
    captcha_text = pytesseract.image_to_string(img, config='--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

    return captcha_text.strip()

# 测试验证码识别
captcha_image_path = '../res/verify.png'  # 替换为你的验证码图片路径
recognized_text = recognize_captcha(captcha_image_path)
print(f"识别到的验证码: {recognized_text}")
