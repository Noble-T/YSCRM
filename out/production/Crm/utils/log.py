#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/3/30 10:27 
@Author  :
@File    : log.py.py
@ProjectName: CRM 
'''
import logging

# 创建日志记录器
import os
import time

logger = logging.getLogger()
# logger 的等级
logger.setLevel(logging.INFO)
# 创建一个 handler，写入日志文件
log_path = '../logs/'
if not os.path.exists(log_path):
    os.makedirs(log_path)

log_file_name = log_path + 'logs-' + time.strftime("%Y%m%d", time.localtime()) + '.log'
fh = logging.FileHandler(log_file_name, mode='a+', encoding='utf-8')
fh.setLevel(logging.INFO)
# 设置日志输出格式
format = logging.Formatter('[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(levelname)s] # %(message)s')
fh.setFormatter(format)
# 将 handler 添加到 logger 里面
logger.addHandler(fh)
logger.info("======Start printing logs======")

# 同样的，创建一个Handler用于控制台输出日志
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(format)
logger.addHandler(ch)