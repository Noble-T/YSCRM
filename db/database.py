#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/3/30 14:07 
@Author  :
@File    : database.py
@ProjectName: CRM 
'''
import json
import time

import pymysql
import schedule
from ruamel.yaml import YAML

from utils.log import logger


# def task():
#     print("\nTask executed at:", time.ctime(time.time()))
#     database()


def database():
    try:
        yaml = YAML()
        with open('../conf/config.yaml', 'r', encoding='utf-8') as file:
            # 使用yaml.safe_load()函数读取YAML文件内容
            config_data = yaml.load(file)
            # 使用 json.dumps 来美化输出 JSON 数据，ensure_ascii=False 参数来正确显示中文字符
            pretty_json = json.dumps(config_data, indent=4, ensure_ascii=False)
            print("{}\n".format(pretty_json))

            # 测试环境
            # db = pymysql.connect(host=config_data['mysql']['host'], port=config_data['mysql']['port'], user=config_data['mysql']['user'],
            #                      passwd=config_data['mysql']['password'], db=config_data['mysql']['database'], charset='utf8')
            # 仿真环境
            db = pymysql.connect(host=config_data['mysql']['host'], port=config_data['mysql']['port'], user=config_data['mysql']['user_sim'],
                                 passwd=config_data['mysql']['password_sim'], db=config_data['mysql']['database'], charset='utf8')
            # 创建游标对象
            cursor = db.cursor()

            # app
            db_app = pymysql.connect(host=config_data['mysql']['host'], port=config_data['mysql']['port'], user=config_data['mysql']['user_app'],
                                     passwd=config_data['mysql']['password_app'], db=config_data['mysql']['database_app'], charset='utf8')
            # 创建游标对象
            cursor_app = db_app.cursor()

            input_value = input("请输入 1-unionid查询，2-order_id查询(默认)：")
            if input_value == '1':
                # 根据unionid查询订单
                unionid = config_data['unionid']

                input_sql = input("请输入 1-全量删除，2-退款订单删除(默认)：")
                if input_sql == '1':
                    order_id_sql = "select vwcom.order_id from `crm.abctougu.cn`.v2_work_crm_order_main vwcom where vwcom.unionid = %s;"
                    cursor.execute(order_id_sql, unionid)
                else:
                    # -- 查询已退款订单与升级订单后的作废订单
                    """参数化查询：使用占位符 %s 来代替变量值，并在执行查询时通过元组 (unionid, unionid) 传递实际的值。
                    LIKE 操作符：在LIKE操作符中使用双百分号 %% 替代单百分号 %，这是为了防止潜在的单引号问题。尽管在MySQL中通常使用单百分号 %，但在某些情况下，双百分号 %% 可以避免一些特殊的字符问题。
                    执行查询：使用cursor.execute()执行SQL查询，并传入参数化的值。
                    获取结果：使用cursor.fetchall()获取所有结果。"""
                    order_id_sql = "select vwcom.order_id \
                        from `crm.abctougu.cn`.v2_work_crm_order_main vwcom \
                        left join `crm.abctougu.cn`.v2_work_crm_order_main_status vwcoms on vwcom.order_id = vwcoms.order_id \
                        where vwcom.unionid = %s and vwcoms.refund_status = 1 \
                        union \
                        select vwcom.order_id \
                        from `crm.abctougu.cn`.v2_work_crm_order_main_status vwcoms \
                        join `crm.abctougu.cn`.v2_work_crm_order_main vwcom on vwcoms.kill_order COLLATE utf8mb4_unicode_ci LIKE CONCAT('%%', vwcom.order_id, '%%') \
                        where vwcom.unionid = %s and vwcoms.refund_status = 1;"
                    cursor.execute(order_id_sql, (unionid, unionid))
                order_values = cursor.fetchall()
                order_values = [order_value[0] for order_value in order_values]
            else:
                # 根据order_id查询订单
                order_values = config_data['order_id'].split(',')
            # print("\n{}".format(order_values))
            logger.info(f"退款订单id列表：{order_values}")
            for order_value in order_values:
                if order_value != '':
                    last_order_value = order_value
                    # print("\n{}".format(order_value))
                    logger.info(f"\n退款订单号：{order_value}")

                    # 查询unionid并执行
                    query_unionid = "SELECT spare_unionid,kill_order FROM `crm.abctougu.cn`.v2_work_crm_order_main_status WHERE order_id = %s;"
                    cursor.execute(query_unionid, order_value)

                    # 获取单条记录
                    result = cursor.fetchone()
                    if result:  # 判断查询结果是否为空
                        # 将查询结果存储在变量中
                        result_unionid = result[0]
                        result_kill_order = result[1]
                        logger.info(f"退款订单unionid：{result_unionid}，kill_order：{result_kill_order}")

                    # 查询主订单并执行
                    query_order = "SELECT * FROM `crm.abctougu.cn`.v2_work_crm_order_main WHERE order_id = %s;"
                    cursor.execute(query_order, order_value)
                    # 获取所有结果
                    results = cursor.fetchall()
                    print("类型：", type(results))
                    # for row in results:
                    #     print(f"主订单数据: {row}")
                    logger.info("v2_work_crm_order_main 数据列表：\n{}\n".format(results))

                    # 查询子订单并执行
                    query_sub_order = "SELECT * FROM `crm.abctougu.cn`.v2_work_crm_order_main_son WHERE order_id = %s;"
                    cursor.execute(query_sub_order, order_value)
                    # 获取所有结果
                    results = cursor.fetchall()
                    logger.info("v2_work_crm_order_main_son 数据列表：\n{}\n".format(results))

                    # 查询订单状态并执行
                    query_order_status = "SELECT * FROM `crm.abctougu.cn`.v2_work_crm_order_main_status WHERE order_id = %s;"
                    cursor.execute(query_order_status, order_value)
                    # 获取所有结果
                    results = cursor.fetchall()
                    logger.info("v2_work_crm_order_main_status 数据列表：\n{}\n".format(results))

                    # 查询合规并执行
                    query_hegui = "SELECT * FROM `crm.abctougu.cn`.v2_work_crm_hegui WHERE order_id = %s;"
                    cursor.execute(query_hegui, order_value)
                    results = cursor.fetchall()
                    logger.info("v2_work_crm_hegui 数据列表：\n{}\n".format(results))

                    # 查询合同表并执行
                    query_contract = "SELECT * FROM `crm.abctougu.cn`.v2_work_crm_order_contract WHERE order_id = %s;"
                    cursor.execute(query_contract, order_value)
                    results = cursor.fetchall()
                    logger.info("v2_work_crm_order_contract 数据列表：\n{}\n".format(results))


                    # CRM系统-风险测评表
                    risk_id_sql = "select vwcor.id from `crm.abctougu.cn`.v2_work_crm_order_risk vwcor where vwcor.order_id = %s;"
                    cursor.execute(risk_id_sql, order_value)
                    risk_id_results = cursor.fetchall()
                    if len(risk_id_results) != 0:
                        for risk_id_result in risk_id_results:
                            risk_id = risk_id_result[0]
                            # print(risk_id)
                            logger.info(f"风险测评id：{risk_id}")
                            # 删除风险测评子表并执行
                            delete_sub_risk = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_risk_son WHERE p_id = %s;"
                            cursor.execute(delete_sub_risk, risk_id)

                    # CRM系统-退款表
                    refund_id_sql = "select vwcor.id from `crm.abctougu.cn`.v2_work_crm_order_refund vwcor where vwcor.order_id = %s;"
                    cursor.execute(refund_id_sql, order_value)
                    refund_id_results = cursor.fetchall()
                    if len(refund_id_results) != 0:
                        for refund_id_result in refund_id_results:
                            refund_id = refund_id_result[0]
                            # print(refund_id)
                            logger.info(f"退款id：{refund_id}")
                            # 删除退款子表并执行
                            delete_sub_refund = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_refund_son WHERE p_id = %s;"
                            cursor.execute(delete_sub_refund, refund_id)

                    # 删除主订单并执行
                    delete_order = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_main WHERE order_id = %s;"
                    cursor.execute(delete_order, order_value)
                    # 删除子订单并执行
                    delete_sub_order = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_main_son WHERE order_id = %s;"
                    cursor.execute(delete_sub_order, order_value)
                    # 删除订单状态并执行
                    delete_order_status = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_main_status WHERE order_id = %s;"
                    cursor.execute(delete_order_status, order_value)
                    # 删除合规并执行
                    delete_hegui = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_hegui WHERE order_id = %s;"
                    cursor.execute(delete_hegui, order_value)
                    # 删除合规审核记录并执行
                    delete_hegui_log = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_hegui_log WHERE order_id = %s;"
                    cursor.execute(delete_hegui_log, order_value)
                    # 删除合同表并执行
                    delete_contract = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_contract WHERE order_id = %s;"
                    cursor.execute(delete_contract, order_value)
                    # 删除CRM系统-合规退款补充合同操作日志表并执行
                    delete_contract_log = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_compliance_contract_log WHERE order_id = %s;"
                    cursor.execute(delete_contract_log, order_value)
                    # 删除风险测评并执行
                    delete_risk = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_risk WHERE order_id = %s;"
                    cursor.execute(delete_risk, order_value)

                    # 删除退款并执行
                    delete_refund = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_refund WHERE order_id = %s;"
                    cursor.execute(delete_refund, order_value)

                    # 删除多次退款表并执行
                    delete_multiple_refund = "DELETE FROM `crm.abctougu.cn`.multiple_refund WHERE order_id = %s;"
                    cursor.execute(delete_multiple_refund, order_value)

                    # 删除线下付款表并执行
                    delete_offline_pay = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_pay_offline WHERE order_id = %s;"
                    cursor.execute(delete_offline_pay, order_value)
                    # 删除线下付款子表并执行
                    delete_sub_offline_pay = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_pay_offline_son WHERE order_id = %s;"
                    cursor.execute(delete_sub_offline_pay, order_value)
                    # 删除线下退款凭证表并执行
                    delete_offline_refund_voucher = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_refund_offline_son WHERE order_id = %s;"
                    cursor.execute(delete_offline_refund_voucher, order_value)

                    # 删除发票
                    delete_invoice = "DELETE FROM `crm.abctougu.cn`.v2_work_crm_order_invoice_hand WHERE order_id = %s;"
                    cursor.execute(delete_invoice, order_value)

                    # v2_work_crm_order_main_status表中最后一个审核通过订单的is_cancellation（订单是否作废 0：正常 1：作废）更新为0
                    # 将字符串转换为元组
                    # print("result_kill_order：", result_kill_order)
                    if 'result_kill_order' in locals() and result_kill_order: # 判断变量是否存在且不为空
                        order_ids = tuple(result_kill_order.split(','))
                        logger.info(f"order_ids:{order_ids}")
                        update_is_cancellation = "UPDATE `crm.abctougu.cn`.v2_work_crm_order_main_status SET is_cancellation = 0 WHERE order_id IN %s;"
                        cursor.execute(update_is_cancellation, (order_ids,))
                        logger.info("更新v2_work_crm_order_main_status表is_cancellation成功！")

                    # 提交事务
                    db.commit()


                    # 查询unionid并执行
                    query_unionid = "SELECT unionid FROM `crm.abctougu.cn`.v2_work_crm_order_main WHERE order_id = %s;"
                    cursor.execute(query_unionid, order_value)
                    # 获取单条记录
                    result = cursor.fetchone()
                    if result:  # 判断查询结果是否为空
                        # 将查询结果存储在变量中
                        result_unionid = result[0]
                        print("unionid:", result_unionid)



                    # app
                    # 查询合同并执行
                    query_contract = "SELECT * FROM `stock-rubik-cube`.contract_new WHERE order_id = %s;"
                    cursor_app.execute(query_contract, order_value)
                    # 获取所有结果
                    results = cursor_app.fetchall()
                    logger.info("app `stock-rubik-cube`.contract_new数据列表：\n{}\n".format(results))
                    if len(results) != 0:
                        for result in results:
                            if result != '':
                                logger.info("app `stock-rubik-cube`.contract_new数据：\n{}\n".format(result))

                    # 系统用户表
                    order_sql = "select o.user_id from `stock-rubik-cube`.`order` o where o.order_id = %s;"
                    cursor_app.execute(order_sql, order_value)
                    # 获取所有结果
                    order_results = cursor_app.fetchall()
                    logger.info("app `stock-rubik-cube`.`order`数据列表：\n{}\n".format(order_results))

                    # 获取sql结果第三个参数
                    for order_result in order_results:
                        if order_result != '':
                            # logger.info("app订单数据：\n{}\n".format(order_result))
                            user_id = order_result[0]
                            logger.info(f"app用户id：{user_id}\n")
                            # 删除合同
                            delete_contract = "DELETE FROM `stock-rubik-cube`.contract_new WHERE user_id = %s and order_id = %s;"
                            cursor_app.execute(delete_contract, (user_id, order_value))
                            # 删除订单
                            delete_order = "DELETE FROM `stock-rubik-cube`.`order` WHERE user_id = %s and order_id = %s;"
                            cursor_app.execute(delete_order, (user_id, order_value))

                    # user_id_sql = "select o.user_id from `stock-rubik-cube`.`order` o where o.order_id = %s;"
                    # cursor_app.execute(user_id_sql, order_value)
                    # user_id_results = cursor_app.fetchall()
                    # if len(user_id_results) != 0:
                    #     for user_id_result in user_id_results:
                    #         user_id = user_id_result[0]
                    #         # print(refund_id)
                    #         logger.info(f"app用户id：{user_id}\n")
                    #         # 删除合同
                    #         delete_contract = "DELETE FROM `stock-rubik-cube`.contract_new WHERE user_id = %s and order_id = %s;"
                    #         cursor_app.execute(delete_contract, (user_id, order_value))
                    #         # 删除订单
                    #         delete_order = "DELETE FROM `stock-rubik-cube`.`order` WHERE user_id = %s and order_id = %s;"
                    #         cursor_app.execute(delete_order, (user_id, order_value))

                    # 查询用户订单表
                    query_user_order = "SELECT * FROM `stock-rubik-cube`.user_order_product WHERE order_id = %s;"
                    cursor_app.execute(query_user_order, order_value)
                    # 获取所有结果
                    user_order_results = cursor_app.fetchall()
                    logger.info("app `stock-rubik-cube`.user_order_product数据列表：\n{}\n".format(user_order_results))

                    # 删除用户订单表
                    delete_user_order = "DELETE FROM `stock-rubik-cube`.user_order_product WHERE order_id = %s;"
                    cursor_app.execute(delete_user_order, order_value)
            # app
            # 提交事务
            db_app.commit()
            # 关闭游标和连接
            cursor_app.close()
            db_app.close()

            if 'result_unionid' in locals() and result_unionid: # 判断变量是否存在
                # 检查记录是否存在
                cursor.execute("SELECT vwcom.service_end_add_time \
                            FROM `crm.abctougu.cn`.v2_work_crm_order_main vwcom \
                            LEFT JOIN `crm.abctougu.cn`.v2_work_crm_order_main_status vwcoms ON vwcom.order_id = vwcoms.order_id \
                            WHERE vwcom.unionid = %s AND vwcoms.hg_status = 1 \
                            ORDER BY vwcoms.hg_time DESC \
                            LIMIT 1", (result_unionid,))
                record = cursor.fetchone()
                logger.info(f"{result_unionid}用户到期时间：{record}")
                if record:
                    # 记录存在，执行更新操作
                    # work_crm_base_user表中u_expire_date（用户到期时间）更新为v2_work_crm_order_main（订单表）中最后一个审核通过订单的service_end_add_time（服务到期时间）
                    update_user_expire_date = "UPDATE `crm.abctougu.cn`.work_crm_base_user \
                                            SET u_expire_date = (\
                                                SELECT vwcom.service_end_add_time \
                                                FROM `crm.abctougu.cn`.v2_work_crm_order_main vwcom \
                                                LEFT JOIN `crm.abctougu.cn`.v2_work_crm_order_main_status vwcoms ON vwcom.order_id = vwcoms.order_id \
                                                WHERE vwcom.unionid = %s AND vwcoms.hg_status = 1 \
                                                ORDER BY vwcoms.hg_time DESC \
                                                LIMIT 1) \
                                            WHERE unionid = %s;"
                    cursor.execute(update_user_expire_date, (result_unionid, result_unionid))
                    logger.info("更新work_crm_base_user表u_expire_date成功！")

            # 删除黑名单
            # 生产：owAkH6pzIm8b-ToOmC0cz7p2IomI，仿真：o1ELc6LrAZOqCjYiOZur5A-sVzYc
            delete_blacklist = ("DELETE FROM `crm.abctougu.cn`.work_crm_blacklist WHERE value IN ('owAkH6pzIm8b-ToOmC0cz7p2IomI', \
                                'o1ELc6LrAZOqCjYiOZur5A-sVzYc', 'owAkH6hLuQM8nATHzmdM8n-qigCg', 'o1ELc6C-o91OlKbgUIPaGGMgS858', 'oAESl0QRB8mndRVJFs69e5o8JZi0', '13325171563', '320324199504180352', \
                                'oAESl0aF5qnVf6e1G7I15_QKaf8U', '18302954019', '610121199302072600');")
            cursor.execute(delete_blacklist)
            # 提交事务

            db.commit()
            # 关闭游标和连接
            cursor.close()
            db.close()

        #     # 将order_id新值写入config.yaml文件
        #     config_data['order_id'] = '00000000001,'
        # with open('config.yaml', 'w', encoding='utf-8') as file:
        #     yaml.dump(config_data, file)  # 将Python中的字典或者列表转化为yaml格式的数据

    except Exception as e:
        logger.error(f"数据库操作时发生错误: {e}")
        logger.error(f"Error occurred: {e}", exc_info=True)
        return None



database()
# # 每3分钟执行一次task函数
# schedule.every(3).minutes.do(task)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)  # 防止CPU占用过