#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/4/1 9:50 
@Author  : 
@File    : check_excel_data_opt01.py
@ProjectName: CRM 
'''

import os
import pandas as pd
import datetime

# 日期格式常量
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_NUM_FORMAT = "%Y%m%d%H%M%S"

def safe_delete_file(file_path):
    """安全删除文件，添加异常处理"""
    try:
        os.remove(file_path)
        print(f"{datetime.datetime.now().strftime(DATE_FORMAT)} 删除文件 {file_path}")
    except OSError as e:
        print(f"无法删除文件 {file_path}: {e}")

def delete_files(folder_path):
    """递归删除文件夹中的所有文件和子文件夹"""
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print(f"{folder_path} 不是一个有效的目录")
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            safe_delete_file(file_path)
        elif os.path.isdir(file_path):
            delete_files(file_path)

def read_csv_with_exception(file_path):
    """读取CSV文件，添加异常处理"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"无法读取 {file_path}: {e}")
        return None

def write_diff_to_excel(df, file_name, output_dir):
    """将数据写入Excel，添加异常处理"""
    try:
        df.to_excel(os.path.join(output_dir, f'{file_name}.xlsx'), index=False)
        print(f"数据已输出到 {os.path.join(output_dir, f'{file_name}.xlsx')}")
    except Exception as e:
        print(f"无法写入 {file_name}: {e}")

def check_data(file_path1, file_path2, output_dir):
    df1 = read_csv_with_exception(file_path1)
    df2 = read_csv_with_exception(file_path2)

    if df1 is None or df2 is None:
        return

    # 合并操作
    same_rows = df1.merge(df2, indicator=True, how='outer').query('_merge == "both"').drop('_merge', axis=1)
    in_df1_not_df2 = df1[~df1.index.isin(same_rows.index)].dropna(subset=df1.columns)
    in_df2_not_df1 = df2[~df2.index.isin(same_rows.index)].dropna(subset=df2.columns)

    # 输出相同行和不同行到Excel
    if same_rows.size != 0:
        write_diff_to_excel(same_rows, 'same_rows', output_dir)
        print(f"相同行已输出到 {os.path.join(output_dir, 'same_rows{}.xlsx'.format(DATE_NUM_FORMAT))}")
    if in_df1_not_df2.size != 0:
        write_diff_to_excel(in_df1_not_df2, 'diff_in_df1', output_dir)
        print(f"df1中特有的行已输出到 {os.path.join(output_dir, 'diff_in_df1{}.xlsx'.format(DATE_NUM_FORMAT))}")
    if in_df2_not_df1.size != 0:
        write_diff_to_excel(in_df2_not_df1, 'diff_in_df2', output_dir)
        print(f"df2中特有的行已输出到 {os.path.join(output_dir, 'diff_in_df2{}.xlsx'.format(DATE_NUM_FORMAT))}")

# 使用方法
delete_files(r'D:\亚商\数据核对')
check_data(r'D:\亚商\ROI统计_总ROI_2023-03_按公司.csv', r'D:\亚商\ROI统计Task_总ROI_2023-03_按公司.csv', r'D:\亚商\数据核对')