#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/8/27 14:47 
@Author  : 
@File    : delete_files.py
@ProjectName: CRM 
'''
import os
import re


def delete_files(dir_path, file_pattern):
    """
    删除指定目录下文件名中包含特定模式的所有文件。

    :param dir_path: 要搜索的目录路径
    :param file_pattern: 文件名中要匹配的模式
    """
    # 编译正则表达式
    regex = re.compile(file_pattern)

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            # 检查文件名是否匹配模式
            if regex.search(file):
                file_path = os.path.join(root, file)
                print(f"Deleting: {file_path}")
                # os.remove(file_path)


# 使用示例
directory = "D:\\WorkSpaces\\CRM\\res"  # 替换为实际的目录路径
pattern = r"CRM"  # 匹配包含 "bad" 的文件名

delete_files(directory, pattern)
