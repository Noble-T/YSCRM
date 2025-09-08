#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/4/17 14:38 
@Author  : 
@File    : img.py
@ProjectName: CRM 
'''
import re

import cv2
import numpy as np
import pytesseract


# def recognize_captcha(captcha_image_path):
#     """
#     识别验证码图片中的数字
#     :param captcha_image_path: 验证码图片路径
#     :return: 识别出的数字字符串
#     """
#     # 读取验证码图片
#     img = cv2.imread(captcha_image_path)
#
#     # 预处理图片
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转为灰度图
#     blur = cv2.GaussianBlur(gray, (5, 5), 0)       # 应用高斯模糊
#
#     # 可选：尝试其他预处理方法，如阈值化
#     # _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#
#     # 使用pytesseract进行文字识别
#     captcha_text = pytesseract.image_to_string(blur, lang='eng', config='--psm 6 -c tessedit_char_whitelist=0123456789')
#     print("验证码：", captcha_text)
#
#     # 去除多余空格并返回纯数字字符串
#     captcha_text = captcha_text.strip().replace(" ", "")
#
#     return captcha_text
#
#
# captcha_image_path = "pic1.png"
# result = recognize_captcha(captcha_image_path)
# print("识别出的验证码为:", result)


def cv_show(img,name):
    cv2.imshow(name,img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def recognize_english_captcha(captcha_image_path):
    """
    识别英文验证码图片中的文字
    :param captcha_image_path: 验证码图片路径
    :return: 识别出的英文数字字符串
    """
    # 读取验证码图片
    img = cv2.imread(captcha_image_path)

    # 预处理图片
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转为灰度图
    blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 应用高斯模糊
    # canny = cv2.Canny(blur, 0, 300)  # 应用边缘检测
    # v1 = cv2.Canny(canny, 50, 150)
    # v2 = cv2.Canny(canny, 50, 100)
    #
    # res = np.hstack((v1, v2))
    # cv_show(res, 'res')

    # 可选：尝试其他预处理方法，如阈值化
    # _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # cv_show(thresh, 'thresh')

    # 使用pytesseract进行文字识别，配置针对英文识别
    captcha_text = pytesseract.image_to_string(blur, config='--psm 6')
    print("验证码：", captcha_text)

    # # 去除多余空格并返回识别结果
    # captcha_text = captcha_text.strip().replace(" ", "")
    # pattern = r'[A-Za-z0-9]+'   # 匹配英文字母和数字
    captcha_text = re.findall(r'[A-Za-z0-9]+', captcha_text)     # 使用正则表达式匹配英文字母和数字
    return ''.join(captcha_text)    # 将匹配结果连接成一个字符串


captcha_image_path = "res/verify.png"
result = recognize_english_captcha(captcha_image_path)
print("识别出的验证码为:", result)


import base64


def save_base64_image(base64_data, save_path):
    """
    将Base64编码的图片数据保存为本地文件。

    参数:
    base64_data (str): Base64编码的图片数据。
    save_path (str): 保存图片的本地路径（包括文件名及扩展名）。
    """
    # 去掉Base64数据前缀（通常是"data:image/<格式>;base64,"）
    if base64_data.startswith('data:image/'):
        content_type, base64_data = base64_data.split(',')  # 分割出Content-Type和Base64数据
        # 根据Content-Type设置文件扩展名（如果需要）
        # 例如，content_type = 'image/png'，则扩展名为'.png'
        # save_path += '.' + content_type.split('/')[-1]

    # 解码Base64数据为字节串
    image_data = base64.b64decode(base64_data)

    # 将字节串写入文件
    with open(save_path, 'wb') as f:
        f.write(image_data)

# # 示例调用
# base64_encoded_image = "data:image/png;base64,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"
#
# # 替换成实际的Base64编码
# save_path = "D:\\WorkSpaces\\CRM\\res\\verify.png"  # 或者指定其他合适的文件名和扩展名
# save_base64_image(base64_encoded_image, save_path)

