#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/11/13 11:27 
@Author  : 
@File    : generate_passwords.py
@ProjectName: CRM 
'''
import random
import string


# 1.简单密码：仅包含小写字母和数字。
def generate_simple_password(length=8):
   characters = string.ascii_lowercase + string.digits
   password = ''.join(random.choice(characters) for _ in range(length))
   return password

print(generate_simple_password())


# 2.中等复杂度密码：包含大小写字母、数字。
def generate_medium_password(length=12):
   characters = string.ascii_letters + string.digits
   password = ''.join(random.choice(characters) for _ in range(length))
   return password

print(generate_medium_password())


# 3.高复杂度密码：包含大小写字母、数字以及特殊字符。
def generate_complex_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

print(generate_complex_password())


# 4.确保密码强度：生成的密码至少包含一个小写字母、一个大写字母、一个数字和一个特殊字符
def generate_strong_password(length=16):
    if length < 4:
       raise ValueError("密码长度必须至少为4")
    password = [
       random.choice(string.ascii_lowercase),
       random.choice(string.ascii_uppercase),
       random.choice(string.digits),
       random.choice(string.punctuation)
    ]
    remaining_length = length - 4
    characters = string.ascii_letters + string.digits + string.punctuation
    password += [random.choice(characters) for _ in range(remaining_length)]
    random.shuffle(password)
    return ''.join(password)

print(generate_strong_password())


