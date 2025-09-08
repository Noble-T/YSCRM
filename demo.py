#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/4/1 17:56 
@Author  : 
@File    : demo.py
@ProjectName: CRM 
'''
import datetime

from utils.utils import update_config, read_config

date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
date_num = datetime.datetime.now().strftime("%Y%m%d%H")
print(date, date_num)


roi_old = ['生产_ROI统计_按公司_总ROI202404011705.csv', '生产_ROI统计_按公司_前端ROI202404011705.csv', '生产_ROI统计_按公司_复购ROI202404011705.csv', '生产_ROI统计_按公司_客服ROI202404011705.csv']
roi_task = ['生产_ROI统计_按公司_总ROI202404011705.csv', '生产_ROI统计_按公司_前端ROI202404011705.csv', '生产_ROI统计_按公司_复购ROI202404011705.csv', '生产_ROI统计_按公司_客服ROI202404011705.csv']

for i in range(len(roi_old)):
    print(i)


file_path_source = r'D:\亚商'
file_path_diff = r'D:\亚商\数据核对'
file_name = '生产-数据核对结果'

i = 0
for roi_old, roi_task in zip(roi_old, roi_task):
    i = i + 1
    # check_data('{}\\{}'.format(file_path, roi_old), '{}\\{}'.format(file_path, roi_task), file_path_diff)
print('{}\\{}'.format(file_path_source, roi_old), '{}\\{}'.format(file_path_source, roi_task), file_path_diff)

# config_datas = read_config('conf/config.yaml')
# print(config_datas)
# update_config('conf/config.yaml', config_datas, 'order_id', 'admin111')
# print(config_data)
# cookies = config_data['crm']['cookie']
# print(len(cookies), cookies)
# cookies_list = list(cookies.keys())
# print(cookies_list[0])
#
# # print(read_config(['crm']['cookie']['value']))
#
# modify_config("config.yaml", 'username', 'admin1')
# print(a)





# dictionary = {'order_id': '20240330110225280253,', 'mysql': {'database': 'crm.abctougu.cn', 'host': 'ysjumpserver.abctougu.com', 'password': 'U2ABsLefzKM814vO', 'port': 33061, 'user': 'b216af38-812f-457e-bfb7-98d1c61096d5'}, 'crm': {'url': 'https://pay.oneil88.com/admin', 'username': '酷酷酷', 'password': 123456, 'cookie': {'name': 'jmftou', 'value': 'a4152224628ba20e86799f7544cafa1c'}}}

# print((config_data))
# modify_config('config.yaml', config_data)
#
# def replace_key_in_dict(dictionary, target_key, new_value):
#     for key, value in dictionary.items():
#         if isinstance(value, dict):
#             replace_key_in_dict(value, target_key, new_value)
#         elif key == target_key:
#             dictionary[key] = new_value
# replace_key_in_dict(dictionary, 'username', 'admin1')
#
# # 遍历嵌套字典或list并替换字典的key
# def update_allvalues(dictionary,key,value):
#     if isinstance(dictionary, dict):  # 使用isinstance检测数据类型，如果是字典
#         print('字典')
#         if key in dictionary.keys():  # 替换字典第一层中所有key与传参一致的key
#             dictionary[key] = value
#         for k in dictionary.keys():   # 遍历字典的所有子层级，将子层级赋值为变量chdict，分别替换子层级第一层中所有key对应的value，最后在把替换后的子层级赋值给当前处理的key
#             chdict = dictionary[k]
#             update_allvalues(chdict,key,value)
#             dictionary[k] = chdict
#     elif isinstance(dictionary, list):  # 如是list
#         print('列表')
#         for element in dictionary:   # 遍历list元素，以下重复上面的操作
#             if isinstance(element, dict):
#                 if key in element.keys():
#                     element[key] = value
#                 for k in element.keys():
#                     chdict = element[k]
#                     update_allvalues(chdict,key,value)
#                     element[k] = chdict
# update_allvalues(dictionary,'username','admin1')
# print(dictionary)



import re

# 定义待处理字符串
text = "abc123def456ghi"

# 使用正则表达式提取数字。使用re.findall()函数，传入一个匹配数字的正则表达式模式，并指定要搜索的字符串。在这里，模式"\d+"代表一个或多个连续的数字字符（\d代表任何十进制数字，+表示一个或多个重复）
num_list = re.findall(r"\d+", text)
result_str = ''
for num in num_list:
    print(num)
    result_str = result_str+str(num)
    print(result_str)

# 查看提取结果
print(num_list)


x = -100.00
abs_x = abs(x) # 返回x的绝对值
print(abs_x)

a = "222.22a"
print(a.isdigit())

num1 = "123%"
num2 = "0"
num3 = "()-"
print(eval(num1.strip('%'))-eval(num2.strip('%')))
def is_number(s):
    try:
        float(s)  # 尝试转换为浮点数，这会接受整数、浮点数，甚至是科学计数法
        return True
    except ValueError:
        return False

s = "123.45%"
if is_number(s):
    print("是数字")
else:
    print("不是数字")


# 使用高斯模糊和Otsu阈值化
import cv2
import numpy as np

def preprocess_image(image_path):
    # 读取图像
    image = cv2.imread(image_path)

    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 高斯模糊
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu阈值化
    _, thresh = cv2.threshold()


input_string = "example:   data to be extracted   "

# 截取冒号之后的数据
colon_index = input_string.index(":")
substring_after_colon = input_string[colon_index + 1:]

# 清除截取部分的空格
cleared_data = substring_after_colon.strip()

print(cleared_data)



for i in range(1, 4):
    print(i)
