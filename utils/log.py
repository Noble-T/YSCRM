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



# import logging
# import os
# import time
# from logging.handlers import TimedRotatingFileHandler
#
# def configure_logger(log_path="../logs/", log_level=logging.INFO):
#     """
#     配置日志记录器
#     :param log_path: 日志存储路径，默认为 ../logs/
#     :param log_level: 日志级别，默认为 INFO
#     """
#     # 确保日志目录存在
#     try:
#         if not os.path.exists(log_path):
#             os.makedirs(log_path)
#     except Exception as e:
#         print(f"创建日志目录失败: {e}")
#         return
#
#     # 创建日志记录器
#     logger = logging.getLogger()
#     logger.setLevel(log_level)
#
#     # 定义日志格式
#     log_format = logging.Formatter(
#         '[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(levelname)s] # %(message)s'
#     )
#
#     # 配置文件日志处理器（按天轮转）
#     log_file_name = os.path.join(log_path, 'logs-' + time.strftime("%Y%m%d", time.localtime()) + '.log')
#     file_handler = TimedRotatingFileHandler(log_file_name, when='midnight', interval=1, backupCount=7, encoding='utf-8')
#     file_handler.suffix = "%Y-%m-%d"
#     file_handler.setLevel(log_level)
#     file_handler.setFormatter(log_format)
#     logger.addHandler(file_handler)
#
#     # 配置控制台日志处理器
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(log_level)
#     console_handler.setFormatter(log_format)
#     logger.addHandler(console_handler)
#
#     # 记录日志开始信息
#     logger.info("======Start printing logs======")
#
#
# # 调用日志配置函数
# if __name__ == "__main__":
#     configure_logger()
