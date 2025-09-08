#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/3/29 15:24 
@Author  : admin
@File    : check_excel_data2024032901.py
@ProjectName: CRM 
'''
import pandas as pd


# 读取第一个文件
df1 = pd.read_csv(r'D:\亚商\ROI统计_总ROI_2023-03_按公司.csv')

# 读取第二个文件
df2 = pd.read_csv(r'D:\亚商\ROI统计Task_总ROI_2023-03_按公司.csv')

# 找到两个文件中完全相同的行
same_rows = df1.merge(df2, indicator=True, how='outer').query('_merge == "both"').drop('_merge', axis=1)


# 找到在df1中但不在df2中的行
in_df1_not_df2 = df1[~df1.index.isin(same_rows.index)].dropna(subset=df1.columns)

# 找到在df2中但不在df1中的行
in_df2_not_df1 = df2[~df2.index.isin(same_rows.index)].dropna(subset=df2.columns)

if same_rows.size != 0:
    # 输出相同行到新Excel文件
    same_rows.to_excel(r'D:\亚商\数据核对\same_rows.xlsx', index=False)

if in_df1_not_df2.size != 0:
    # 输出df1中特有的行到新Excel文件
    in_df1_not_df2.to_excel(r'D:\亚商\数据核对\diff_in_df1.xlsx', index=False)

if in_df2_not_df1.size != 0:
    # 输出df2中特有的行到新Excel文件
    in_df2_not_df1.to_excel(r'D:\亚商\数据核对\diff_in_df2.xlsx', index=False)




import pandas as pd

def compare_and_export_data(file_path1, file_path2, output_dir):
    # 使用变量代替硬编码路径
    try:
        # 读取文件
        df1 = pd.read_csv(file_path1)
        df2 = pd.read_csv(file_path2)

        # 找到两个文件中完全相同的行
        same_rows = df1.merge(df2, indicator=True, how='outer').query('_merge == "both"').drop('_merge', axis=1)

        # 找到在df1中但不在df2中的行
        in_df1_not_df2 = df1[~df1.index.isin(same_rows.index)].dropna(subset=df1.columns)

        # 找到在df2中但不在df1中的行
        in_df2_not_df1 = df2[~df2.index.isin(same_rows.index)].dropna(subset=df2.columns)

        # 输出相同行到新Excel文件
        export_to_excel(same_rows, output_dir, 'same_rows')

        # 输出df1中特有的行到新Excel文件
        export_to_excel(in_df1_not_df2, output_dir, 'diff_in_df1')

        # 输出df2中特有的行到新Excel文件
        export_to_excel(in_df2_not_df1, output_dir, 'diff_in_df2')

    except Exception as e:
        print(f"Error occurred: {e}")

def export_to_excel(dataframe, output_dir, filename):
    # 检查文件是否存在并询问是否覆盖
    output_path = f"{output_dir}\{filename}.xlsx"
    if pd.ExcelFile(output_path).sheet_names:
        proceed = input(f"The file {filename}.xlsx already exists. Do you want to overwrite it? (Y/N): ")
        if proceed.lower() != 'y':
            return

    try:
        dataframe.to_excel(output_path, index=False)
        print(f"{filename}.xlsx exported successfully.")
    except Exception as e:
        print(f"Error exporting {filename}.xlsx: {e}")

# 调用函数，并使用变量代替硬编码路径
compare_and_export_data(r'D:\亚商\ROI统计_总ROI_2023-03_按公司.csv', r'D:\亚商\ROI统计Task_总ROI_2023-03_按公司.csv', r'D:\亚商\数据核对')
