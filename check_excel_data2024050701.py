#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/5/7 9:20 
@Author  : 
@File    : check_excel_data2024050701.py
@ProjectName: CRM 
'''
import datetime
import os

import pandas as pd


date_num = datetime.datetime.now().strftime("%Y%m%d%H%M")
def check_data(file_path1, file_path2, output_dir):
    df1 = pd.read_csv(file_path1, encoding='GB18030') # 读取csv文件，并指定编码格式为GB18030
    # df1 = pd.read_csv(file_path1)
    # df1 = df1.applymap(lambda x: x.encode('utf-8').decode('utf-8') if isinstance(x, str) else x) # 将中文字符转换为utf-8编码
    df1.fillna('', inplace=True)     # 将空值替换为''
    df2 = pd.read_csv(file_path2, encoding='GB18030') # 读取csv文件，并指定编码格式为GB18030
    # df2 = pd.read_csv(file_path2)
    df2.fillna('', inplace=True)

    # 使用merge函数找出两个DataFrame中相同的数据
    # how='inner' 表示只保留两个DataFrame中都有的行（即交集）
    common_data = pd.merge(df1, df2, on=df1.columns.tolist(), how='inner')
    common_data = common_data.drop_duplicates()
    print(f"\n\n==========相同数据：\n{common_data}")
    common_data.to_excel(os.path.join(output_dir, 'common_data{}.xlsx'.format(date_num)), index=True, header=True)

    # 找到只在df1中存在的行
    only_in_df1 = df1[~df1.isin(common_data).all(axis=1)]
    only_in_df1.to_excel(os.path.join(output_dir, 'only_in_df1{}.xlsx'.format(date_num)), index=True, header=True)
    print(f"\n\n==========df1中独有数据：\n{only_in_df1}")

    # 找到只在df2中存在的行
    only_in_df2 = df2[~df2.isin(common_data).all(axis=1)]
    only_in_df2.to_excel(os.path.join(output_dir, 'only_in_df2{}.xlsx'.format(date_num)), index=True, header=True)
    print(f"\n\n==========df2中独有数据：\n{only_in_df2}")

    # 按列合并（axis=1）所有差异行的DataFrame
    diff_results = pd.concat([only_in_df1, only_in_df2], ignore_index=False, axis=1)

    # 按列合并（axis=1）所有差异行的DataFrame
    # diff_results = pd.concat([df1, df2], axis=1, ignore_index=True)
    # with pd.ExcelWriter(os.path.join(output_dir, '{}{}-{}.xlsx'.format(file_results, date_num, i))) as writer:
    with pd.ExcelWriter(os.path.join(output_dir, 'common_data{}.xlsx'.format(date_num))) as writer:
        df1.to_excel(writer, sheet_name='old')
        df2.to_excel(writer, sheet_name='new')
        for sheet in common_data, diff_results:
            # sheet.to_excel(writer, sheet_name='核对结果{}'.format(i))
            if sheet is common_data:
                sheet.to_excel(writer, sheet_name='相同数据')
            else:
                sheet.to_excel(writer, sheet_name='差异数据')

        print(f"数据核对结果已输出到 {os.path.join(output_dir, '{}{}-{}.xlsx'.format(file_results, date_num, i))}")



old_data = ['推广_团队数据-前端-202403按公司 - 副本.csv']
new_data = ['推广_团队数据极速版-前端-202403按公司 - 副本.csv']

# old_data = ['推广_团队数据-客服-202403按公司.csv']
# new_data = ['推广_团队数据极速版-客服-202403按公司.csv']


file_path_source = r'D:\亚商'
file_path_diff = r'D:\亚商\数据核对'
file_results = '推广_员工数据-复购-202403按公司-数据核对结果'

i = 0
for old, new in zip(old_data, new_data):
    i = i + 1
    check_data('{}\\{}'.format(file_path_source, old), '{}\\{}'.format(file_path_source, new), file_path_diff)