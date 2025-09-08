# !/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/6/12 16:42 
@Author  : 
@File    : random_text.py
@ProjectName: CRM 
'''
import random
import string

def generate_random_text(length=500):
    """生成一段指定长度的随机文本"""
    # 定义可能的字符集合，包括字母大小写和标点符号以增加多样性
    characters = string.ascii_letters + string.digits + string.punctuation + " "

    # 生成随机文本
    text = ''.join(random.choice(characters) for _ in range(length))

    return text

random_text = generate_random_text(500)
print(random_text)