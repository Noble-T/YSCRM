#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/5/7 11:07 
@Author  : 
@File    : check_excel_data2024050702.py
@ProjectName: CRM 
'''
import datetime
import os

import pandas as pd


date_num = datetime.datetime.now().strftime("%Y%m%d%H%M")
def check_data(file_path1, file_path2, output_dir):
    # df1 = pd.read_csv(file_path1)
    df1 = pd.read_csv(file_path1, encoding='GB18030') # 读取csv文件，并指定编码格式为GB18030
    # df1 = df1.applymap(lambda x: x.encode('utf-8').decode('utf-8') if isinstance(x, str) else x) # 将中文字符转换为utf-8编码
    df1.fillna('', inplace=True)     # 将空值替换为''
    # df2 = pd.read_csv(file_path2)
    df2 = pd.read_csv(file_path2, encoding='GB18030') # 读取csv文件，并指定编码格式为GB18030
    df2.fillna('', inplace=True)

    # 使用merge函数找出两个DataFrame中相同的数据
    # how='inner' 表示只保留两个DataFrame中都有的行（即交集）
    same_diff = pd.merge(df1, df2, on=df1.columns.tolist(), how='inner')
    same_diff = same_diff.drop_duplicates()

    # 找出df1中不在same_diff中的数据（即df1独有的数据）
    unique_to_df1 = df1.merge(df2, how='left', indicator=True).loc[lambda x : x['_merge'] == 'left_only']

    # 找出df2中不在same_diff中的数据（即df2独有的数据）
    unique_to_df2 = df2.merge(df1, how='left', indicator=True).loc[lambda x : x['_merge'] == 'left_only']

    # 删除辅助列 '_merge'
    unique_to_df1.drop(columns=['_merge'], inplace=True)
    unique_to_df2.drop(columns=['_merge'], inplace=True)

    diff_results = pd.concat([unique_to_df1, unique_to_df2], ignore_index=False, axis=1)

    # 导出不同的数据到新的CSV文件
    unique_to_df1.to_excel(os.path.join(output_dir, 'unique_to_df1{}-{}.xlsx'.format( date_num, i)))
    unique_to_df2.to_excel(os.path.join(output_dir, 'unique_to_df2{}-{}.xlsx'.format( date_num, i)))
    diff_results.to_excel(os.path.join(output_dir, 'diff_results{}-{}.xlsx'.format( date_num, i)))

    with pd.ExcelWriter(os.path.join(output_dir, '{}{}-{}.xlsx'.format(file_results, date_num, i))) as writer:
        df1.to_excel(writer, sheet_name='old')
        df2.to_excel(writer, sheet_name='new')
        for sheet in same_diff, diff_results:
            # sheet.to_excel(writer, sheet_name='核对结果{}'.format(i))
            if sheet is same_diff:
                sheet.to_excel(writer, sheet_name='相同数据')
            else:
                sheet.to_excel(writer, sheet_name='差异数据')


old_data = ['推广_团队数据-前端-202403按公司 - 副本.csv']
new_data = ['推广_团队数据极速版-前端-202403按公司 - 副本.csv']

# old_data = ['推广_团队数据-客服-202403按公司.csv']
# new_data = ['推广_团队数据极速版-客服-202403按公司.csv']


file_path_source = r'D:\亚商'
file_path_diff = r'D:\亚商\数据核对'
file_results = '推广_团队数据-前端-202403按公司-副本-数据核对结果'

i = 0
for old, new in zip(old_data, new_data):
    i = i + 1
    check_data('{}\\{}'.format(file_path_source, old), '{}\\{}'.format(file_path_source, new), file_path_diff)