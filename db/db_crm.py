#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/4/18 15:30 
@Author  : 
@File    : db_crm.py
@ProjectName: CRM 
'''

import pymysql

from utils.utils import read_config


def query_system_users(database_host, database_port, username, password, database_name):
    """
    查询crm.abctougu.cn数据库的system_user表，并返回查询结果。

    参数:
    database_host (str): 数据库服务器主机名或IP地址。
    database_port (int): 数据库服务器端口。
    username (str): 数据库登录用户名。
    password (str): 数据库登录密码。
    database_name (str): 数据库名称。

    返回:
    list of dict: 查询结果，每个元素是一个字典，表示一行记录。
    """
    # 创建连接
    connection = pymysql.connect(
        host=database_host,
        port=database_port,
        user=username,
        password=password,
        db=database_name,
        charset='utf8mb4'  # 设置字符集，根据实际情况调整
    )

    try:
        with connection.cursor() as cursor:
            # 执行SQL查询
            query = "select session_id from `crm.abctougu.cn`.`system_user` where username = 'admin';"
            cursor.execute(query)

            # 获取查询结果
            rows = cursor.fetchall()
            print("rows", rows)

            for row in rows:
                print("row", row[0])

            # 将结果转换为列表字典形式
            result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
            print("result", result)

        connection.commit()  # 提交事务（如果查询无写操作，这一步可省略）

        return result

    finally:
        connection.close()  # 关闭连接


config_data = read_config('../conf/config.yaml')
print(config_data)
# 示例调用
host = config_data['mysql']['host']
port = config_data['mysql']['port']
username = config_data['mysql']['user']
password = config_data['mysql']['password']
db_name = config_data['mysql']['database']

system_users = query_system_users(host, port, username, password, db_name)
for user in system_users:
    print("user", user)