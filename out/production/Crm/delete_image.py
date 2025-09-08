#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/8/27 14:31 
@Author  : 
@File    : delete_image.py
@ProjectName: CRM

删除具有相同文件名的多个图片
'''
import os


# def delete_same_files(dir_path):
#     # 获取目录下所有的文件名
#     file_names = os.listdir(dir_path)
#
#     # 创建一个字典来存储每个文件名及其出现次数
#     file_count = {}
#
#     # 统计每个文件名的出现次数
#     for file_name in file_names:
#         if file_name in file_count:
#             file_count[file_name] += 1
#             print(f"Duplicate file name: {file_count, file_name}")
#         else:
#             file_count[file_name] = 1
#             print(f"Unique file name: {file_name}")
#
#     print("File count:", file_count)
#
#     # 遍历字典，删除重复的文件
#     for file_name, count in file_count.items():
#         if count > 1:
#             # 保留第一个文件，删除其余重复的文件
#             base_path = os.path.join(dir_path, file_name)
#             for i in range(1, count):
#                 try:
#                     os.remove(base_path)
#                     print(f"Deleted duplicate file: {base_path}")
#                 except FileNotFoundError:
#                     # 如果文件已经被删除，则跳过
#                     pass
#
#
# # 使用示例
# directory = 'D:\\WorkSpaces\\CRM\\res'  # 替换为实际的目录路径
#
# delete_same_files(directory)


import os
from collections import defaultdict


def delete_duplicate_filenames(dir_path):
    """
    删除具有相同文件名的多个图片，只保留一个副本。

    :param dir_path: 图片所在的目录路径
    """
    # 记录每个文件名及其出现次数
    filename_counts = defaultdict(int)

    # 收集文件名
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            filename_counts[file] += 1
            print(f"{filename_counts[file]} {file}")
    print(filename_counts)

    # 删除多余的文件
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if filename_counts[file] > 1:
                file_path = os.path.join(root, file)
                print(f"Deleting duplicate: {file_path}")
                os.remove(file_path)
                # 减少计数器
                filename_counts[file] -= 1


# 使用示例
directory = "/path/to/your/directory"  # 替换为实际的目录路径

delete_duplicate_filenames(directory)
