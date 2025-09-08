import os
import pymysql
from ruamel.yaml import YAML
from utils.log import logger

yaml = YAML()
with open('../conf/config.yaml', 'r', encoding='utf-8') as file:
    config_data = yaml.load(file)
    # logger.info(f"Config data: {config_data}")


# 封装数据库连接
def get_db_connection(host, port, user, passwd, db):
    return pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')


# 封装查询
def query_records(db, value):
    # 封装查询逻辑为函数，减少重复代码
    tables_to_query = [
        "`v2_work_crm_order_risk`",
        "`v2_work_crm_order_refund`"
    ]
    for table in tables_to_query:
        query_sql = f"SELECT id FROM {table} WHERE order_id = %s;"
        cursor = db.cursor()
        cursor.execute(query_sql, (value,))
        records = cursor.fetchall()
        cursor.close()
        if len(records) != 0:
            for record in records:
                return record[0]
        else:
            return None


def execute_and_commit(db, sql, params=None):
    cursor = db.cursor()
    try:
        cursor.execute(sql, params)
        db.commit()
    except Exception as e:
        logger.error(f"执行SQL出错: {sql}, 参数: {params}, 错误信息:{e}")
        db.rollback()
    finally:
        cursor.close()


def delete_records(db, value):
    # 封装删除逻辑为函数，减少重复代码
    tables_to_delete = [
        "`v2_work_crm_order_risk_son`",
        "`v2_work_crm_order_refund_son`",
        "`v2_work_crm_order_main`",
        "`v2_work_crm_order_main_son`",
        "`v2_work_crm_order_main_status`",
        "`v2_work_crm_hegui`",
        "`v2_work_crm_hegui_log`",
        "`v2_work_crm_order_contract`",
        "`v2_work_crm_order_risk`",
        "`v2_work_crm_order_refund`",
        "`v2_work_crm_order_pay_offline`",
        "`v2_work_crm_order_pay_offline_son`",
        "`v2_work_crm_order_refund_offline_son`"
    ]

    for table in tables_to_delete:
        print(f"删除{table}表")
        # 删除子表并执行
        if table in ["`v2_work_crm_order_risk_son`", "`v2_work_crm_order_refund_son`"]:
            id_sql = query_records(db, value)
            if id_sql is None:
                logger.info(f"{table} 子表id:{id_sql}")
                continue
            else:
                delete_sql = f"DELETE FROM {table} WHERE p_id = %s;"
                execute_and_commit(db, delete_sql, (id_sql,))
                logger.info(f"删除成功,子表id:{id_sql}")
        else:
            if query_records(db, value) is None:
                logger.info(f"{table} 订单id:{value}不存在")
                continue
            else:
                delete_sql = f"DELETE FROM {table} WHERE order_id = %s;"
                execute_and_commit(db, delete_sql, (value,))
                logger.info(f"删除成功,订单id:{value}")


    # # 删除黑名单
    # delete_blacklist = "DELETE FROM `crm.abctougu.cn`.work_crm_blacklist WHERE value IN ('oAESl0QRB8mndRVJFs69e5o8JZi0', '13325171563', '320324199504180352');"
    # cursor = db.cursor()
    # cursor.execute(delete_blacklist)
    # # 提交事务
    # db.commit()
    # # 关闭游标和连接
    # cursor.close()
    # db.close()


def delete_records_app(db, value):
    tables_to_delete = [
        "`contract_new`",
        "`order`"
    ]
    for table in tables_to_delete:
        print(f"删除{table}表")
        # 删除子表并执行
        id_sql = query_records(db, value)
        if id_sql is None:
            logger.info(f"{table} id:{id_sql}不存在")
            continue
        else:
            delete_sql = f"DELETE FROM {table} WHERE order_id = %s;"
            execute_and_commit(db, delete_sql, ())


db = get_db_connection(config_data['mysql']['host'], config_data['mysql']['port'], config_data['mysql']['user'], config_data['mysql']['password'], config_data['mysql']['database'])
db_app = get_db_connection(config_data['mysql']['host'], config_data['mysql']['port'], config_data['mysql']['user_app'], config_data['mysql']['password_app'], config_data['mysql']['database_app'])
try:
    order_values = config_data['order_id'].split(',')
    logger.info(f"订单id列表: {order_values}")
    for order_value in order_values:
        logger.info(f"\n订单id-crm: {order_value}")
        delete_records(db, order_value)

    for order_val in order_values:
        logger.info(f"\n订单id-app: {order_val}")
        delete_records_app(db_app, order_val)
finally:
    db.close()








# import pymysql
# from ruamel.yaml import YAML
#
# from utils.log import logger
#
# yaml = YAML()
# try:
#     with open('../conf/config.yaml', 'r', encoding='utf-8') as file:
#         config_data = yaml.load(file)
# except FileNotFoundError as e:
#     logger.error(f"配置文件找不到：{e}")
#     raise
# except Exception as e:
#     logger.error(f"加载配置文件出错：{e}")
#     raise
#
# # 将数据库配置抽象出来，避免硬编码
# db_config = {
#     'host': config_data['mysql']['host'],
#     'port': config_data['mysql']['port'],
#     'user': config_data['mysql']['user'],
#     'passwd': config_data['mysql']['password'],
#     'db': config_data['mysql']['database'],
#     'charset': 'utf8'
# }
# db_app_config = {
#     'host': config_data['mysql']['host'],
#     'port': config_data['mysql']['port'],
#     'user': config_data['mysql']['user_app'],
#     'passwd': config_data['mysql']['password_app'],
#     'db': config_data['mysql']['database_app'],
#     'charset': 'utf8'
# }
#
# # 使用事务处理和异常捕获来优化数据库操作
# def execute_and_commit(cursor, sql, params=()):
#     try:
#         cursor.execute(sql, params)
#         db.commit()
#     except pymysql.DatabaseError as e:
#         logger.error(f"执行SQL出错：{sql}, {e}")
#         db.rollback()
#         raise
#     except Exception as e:
#         logger.error(f"未知错误：{e}")
#         db.rollback()
#         raise
#
# # 封装删除操作，提高代码复用性
# def delete_from_table(cursor, table_name, column_name, value):
#     sql = f"DELETE FROM `{table_name}` WHERE `{column_name}` = %s;"
#     execute_and_commit(cursor, sql, (value,))
#
# with pymysql.connect(**db_config) as db, db.cursor() as cursor:
#     order_values = config_data['order_id'].split(',')
#     logger.info(f"退款订单id列表：{order_values}")
#     for order_value in order_values:
#         logger.info(f"退款订单id：{order_value}")
#
#         # 执行针对订单的删除操作
#         delete_from_table(cursor, 'v2_work_crm_order_risk', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_refund', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_main', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_main_son', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_main_status', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_hegui', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_hegui_log', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_contract', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_risk', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_refund', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_pay_offline', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_pay_offline_son', 'order_id', order_value)
#         delete_from_table(cursor, 'v2_work_crm_order_refund_offline_son', 'order_id', order_value)
#
#     # 删除黑名单，改进为参数化查询
#     blacklist_values = ('oAESl0QRB8mndRVJFs69e5o8JZi0', '13325171563', '320324199504180352')
#     execute_and_commit(cursor, "DELETE FROM `work_crm_blacklist` WHERE value IN %s", (blacklist_values,))
#
# with pymysql.connect(**db_app_config) as db_app, db_app.cursor() as cursor_app:
# # 对于app相关的数据库操作也可以类似封装和优化
# # ...
#
# # 注意：代码中已省略部分未修改的代码片段，例如日志配置等
