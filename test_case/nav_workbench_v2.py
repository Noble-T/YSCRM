#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    :
# @Author  :
# @File    :
# @ProjectName:
import datetime
import re
import sys
import time

import pyperclip
from pynput.keyboard import Controller, Key
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from utils.log import logger
from utils.utils import read_config, is_element_present, update_config, query, get_current_time


# 跳转到工作台V2
def navigate_to_workbench_v2(driver):
    try:
        # 显式等待
        wait = WebDriverWait(driver, 10)
        element_li = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.layui-header.notselect > ul.layui-nav.layui-layout-left > li:nth-child(4) a > span")))
        driver.execute_script('arguments[0].click()', element_li)
        logger.info("点击工作台V2")
    except Exception as e:
        logger.error(f"跳转到工作台V2发生错误: {e}", exc_info=True)
        driver.save_screenshot("../res/CRM跳转到工作台V2错误{}.jpg".format(get_current_time()))
        # sys.exit()


def compliance_files(driver):
    """
    合规档案
    :param driver:
    :return:
    """
    try:
        wait = WebDriverWait(driver, 20)
        # 点击合规档案菜单
        ele = wait.until(lambda x: driver.find_element(By.XPATH, "(//span[contains(text(),'合规档案')])[2]"))
        driver.execute_script("arguments[0].scrollIntoView();", ele)    # 滚动到元素可见
        ele.click()
        logger.info("点击合规档案菜单")
        # uri_h = driver.current_url
        # # 输入手机号并查询
        # ele = wait.until(lambda x: driver.find_element(By.XPATH, "//input[@placeholder='请输入手机号']"))
        # config_datas = read_config('../conf/config.yaml')
        # ele.send_keys(config_datas['crm']['mobile'])
        # # 点击搜索
        # driver.find_element(By.XPATH, "//button[@class='layui-btn layui-btn-primary']").click()
        # # 断言手机号一天只能查询十次
        # msg = wait.until(lambda x: driver.find_element(By.XPATH, "//div[contains(text(),'手机号一天只能查询十次')]")).text
        # if msg == "手机号一天只能查询十次":
        #     logger.info("手机号一天只能查询十次")
        #     # 清空手机号输入框
        #     ele.clear()
        #     # 输入姓名查询
        #     ele = wait.until(lambda x: driver.find_element(By.XPATH, "//input[@placeholder='请输入客户昵称或备注']"))
        #     ele.send_keys(config_datas['crm']['name'])
        #     # 一天只能查询十消失，点击搜索
        #     time.sleep(5)
        #     ele = wait.until(lambda x: driver.find_element(By.XPATH, "//button[@class='layui-btn layui-btn-primary']"))
        #     ele.click()
        #     logger.info("输入姓名查询")
        # else:
        #     logger.info("输入手机号查询")
        # # 输入姓名查询
        # config_datas = read_config('../conf/config.yaml')
        # ele = wait.until(lambda x: driver.find_element(By.XPATH, "//input[@placeholder='请输入客户昵称或备注']"))
        # ele.send_keys(config_datas['crm']['name'])
        # # 点击搜索
        # ele = wait.until(lambda x: driver.find_element(By.XPATH, "//button[@class='layui-btn layui-btn-primary']"))
        # ele.click()
        # logger.info(f"输入姓名查询：{config_datas['crm']['name']}")
        #
        # # 点击档案详情
        # time.sleep(2)
        # ele = wait.until(lambda x: driver.find_element(By.XPATH, "//a[contains(text(),'详情')]/.."))
        # ele.click()
        # logger.info("进入档案详情")

        # 姓名查询
        query(driver, "name")
        # 获取档案详情地址
        url_archives = driver.current_url
        update_config('../conf/config.yaml', read_config('../conf/config.yaml'), 'url_archives', url_archives)
        # print(f"档案详情url：{url_archives}")
        logger.info(f"档案详情url：{url_archives}")

        ele = wait.until(lambda x: driver.find_element(By.XPATH, "//div[contains(text(),'会话记录')]"))
        # 退款产品
        eles = "(//ul[@class='layui-tab-title'])[1]/li"
        if bool(ele) and is_element_present(driver, By.XPATH, eles):
            ele = wait.until(lambda x: driver.find_elements(By.XPATH, eles))
            count = len(ele)
            print(f"产品套餐。。。。。{count}")
            for i in range(count):
                driver.get(read_config('../conf/config.yaml')['crm']['url_archives'])
                ele = wait.until(lambda x: driver.find_elements(By.XPATH, eles))
                ele[i].click()
                product = f"产品套餐{i+1}：{ele[i].text}"
                # 获取订单号
                text = driver.find_element(By.CSS_SELECTOR, "div.layui-tab-item.layui-show > div > div> span:nth-child(2)").text
                for t in re.findall(r"\d+", text):  # 使用正则表达式提取数字,"\d+"代表一个或多个连续的数字字符
                    print(t, type(t))
                    update_config('../conf/config.yaml', read_config('../conf/config.yaml'), 'order_id', t)
                    update_config('../conf/config.yaml', read_config('../conf/config.yaml'), 'product', ele[i].text)

                    # 判断是否退款,   ''.join(变量.split())=去除全部空格
                    is_refund = "div.layui-tab-item.layui-show > div > div> div > a"
                    order_status = "div.layui-tab-item.layui-show > div > div> div > span:nth-child(1)"
                    refund_status = "div.layui-tab-item.layui-show > div > div> div > span:nth-child(2)"
                    logger.info(f"订单号：{t}，{product}，订单状态：{driver.find_element(By.CSS_SELECTOR, order_status).text}")
                    # print(f"订单号：{t}，{product}，合同状态：{''.join(driver.find_element(By.CSS_SELECTOR, contract_status).text.split())},退款：{''.join(driver.find_element(By.CSS_SELECTOR, refund).text.split())}")
                    if (is_element_present(driver, By.CSS_SELECTOR, is_refund)
                            and "退款" in ''.join(driver.find_element(By.CSS_SELECTOR, is_refund).text.split())
                            and is_element_present(driver, By.CSS_SELECTOR, order_status)
                            and ''.join(driver.find_element(By.CSS_SELECTOR, order_status).text.split())) in ("已到期", "服务中", "待服务", "退款中"):
                    # if is_element_present(driver, By.CSS_SELECTOR, is_refund):
                        if ''.join(driver.find_element(By.CSS_SELECTOR, is_refund).text.split()) == "退款":
                            driver.find_element(By.CSS_SELECTOR, is_refund).click()
                            logger.info(f"订单号：{t}，{product}，点击退款")
                            # 确认退款弹窗
                            wait.until(lambda x: driver.find_element(By.XPATH, "//a[contains(text(),'确认')]")).click()
                            # 点击退款详情

                        time.sleep(2)
                        # 到期订单退款
                        if wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, is_refund)).text == "退款详情" and is_element_present(driver, By.CSS_SELECTOR, refund_status) and driver.find_element(By.CSS_SELECTOR, refund_status).text == "退款中":
                            driver.find_element(By.CSS_SELECTOR, is_refund).click()
                            # print(f"退款详情url：{driver.current_url}")
                            logger.info(f"退款详情url：{driver.current_url}")
                            # 退款
                            refund_audit(driver)
                            # # 签署退款
                            # signature_refunds(driver)
                        # 有效期内退款
                        elif wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, is_refund)).text == "退款详情" and driver.find_element(By.CSS_SELECTOR, order_status).text == "退款中":
                            driver.find_element(By.CSS_SELECTOR, is_refund).click()
                            # print(f"退款详情url：{driver.current_url}")
                            logger.info(f"退款详情url：{driver.current_url}")
                            # 退款
                            refund_audit(driver)
                            # # 签署退款
                            # signature_refunds(driver)

                    time.sleep(3)
        else:
            logger.info("无产品订单")
    except Exception as e:
        logger.error(f"进入合规档案详情发生错误: {e}", exc_info=True)
        driver.save_screenshot("../res/CRM进入合规档案详情错误{}.jpg".format(get_current_time()))
        # sys.exit()


def refund_audit(driver):
    """
    退款
    :param driver:
    :return:
    """
    try:
        logger.info("发起退款")
        # 显性等待
        wait = WebDriverWait(driver, 10)
        # 判断第一次审核是否处理
        ele = wait.until(lambda x: driver.find_element(By.XPATH, "//h4[contains(text(),'一次合规审核人')]"))
        driver.execute_script("arguments[0].scrollIntoView();", ele)    # 滚动到元素可见
        # wait.until(lambda x: driver.find_element(By.XPATH, "//h4[contains(text(),'一次合规审核人')]/../p[@class='review']")) and
        if is_element_present(driver, By.XPATH, "//h4[contains(text(),'一次合规审核人')]/../p[@class='review']"):
            logger.info("第一次审核待处理")
            # 点击退款合同下拉框，选择退款合同
            ele = wait.until(lambda x: driver.find_element(By.ID, "select_tag_name"))
            driver.execute_script("arguments[0].scrollIntoView();", ele)    # 滚动到元素可见
            ele.click()
            wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "#select_tag_name > div > dl > dd:nth-child(2)")).click()

            # 获取退款合同
            text = driver.find_element(By.CSS_SELECTOR, "#select_tag_name > div > dl > dd.layui-this > div > span").text
            update_config('../conf/config.yaml', read_config('../conf/config.yaml'), 'refund_contract', text)
            # 点击收起退款合同下拉框
            ele.click()
            logger.info(f"选择退款合同：{text}")

            # 点击退款原因下拉框，选择退款原因
            driver.find_element(By.CSS_SELECTOR, "#refund_form_item_type > div").click()
            wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "#refund_form_item_type > div > div > dl > dd:nth-child(2)")).click()
            print(driver.find_element(By.CSS_SELECTOR, "#refund_form_item_type > div > div > dl > dd:nth-child(2)").text)
            # 点击退款阶段下拉框，选择退款阶段
            driver.find_element(By.CSS_SELECTOR, "#refund_form_item_stage > div > div > div > input").click()
            wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "#refund_form_item_stage > div > div > dl > dd:nth-child(2)")).click()
            # 点击主要责任下拉框，选择主要责任
            driver.find_element(By.CSS_SELECTOR, "#refund_form_item_duty > div > div > div > input").click()
            wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "#refund_form_item_duty > div > div > dl > dd:nth-child(2)")).click()
            # 获取支付金额并填写退款金额
            # refund_amount = driver.find_element(By.XPATH, "//div[contains(text(),'订单信息')]/..//td[8]").text
            ele = wait.until(lambda x: driver.find_elements(By.XPATH, "//div[contains(text(),'订单信息')]/..//tr/td[10]"))
            count = len(ele)
            print(f"支付订单数量：。。。。。{count}")
            refund_amount = 0
            for i in range(count):
                refund_amount += float(ele[i].text)
            print(f"支付金额：{refund_amount}")
            driver.find_element(By.CSS_SELECTOR, "#amountWrap > div > input:nth-child(1)").clear()
            driver.find_element(By.CSS_SELECTOR, "#amountWrap > div > input:nth-child(1)").send_keys(refund_amount)
            # 退款日期
            driver.find_element(By.ID, "price_date0").click()
            # wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "#layui-laydate4 > div.layui-laydate-footer > div > span.laydate-btns-now")).click()
            wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "div.layui-laydate-footer > div > span.laydate-btns-now")).click()
            # 保存
            driver.find_element(By.XPATH, "//button[contains(text(),'保存')]").click()
            logger.info("提交退款")
            time.sleep(3)
            # # 验证是否保存成功
            # msg = wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "#layui-layer13 > div:nth-child(1)")).text
            # if msg == "提交成功":
            #     logger.info("提交退款成功")
            #     print(driver.current_url)
            # else:
            #     logger.info("提交退款失败")
            if is_element_present(driver, By.XPATH, "//h4[contains(text(),'客户信息')]"):
                logger.info("等待客户信息签署")
                signature_refunds(driver, r'../conf/config.yaml')
        else:
            logger.info("第一次审核已处理，等待客户信息签署")
            signature_refunds(driver, r'../conf/config.yaml')
    except Exception as e:
        logger.error(f"发起退款过程中发生错误: {e}", exc_info=True)
        driver.save_screenshot("../res/CRM发起退款错误{}.jpg".format(get_current_time()))
        # sys.exit()


def signature_refunds(driver, path):
    """
    签署退款，跳过 客户信息签署和合规二审
    :param path:
    :param driver:
    :return:
    """
    try:
        # 显性等待
        wait = WebDriverWait(driver, 10)
        # 判断客户信息是否完善 //h4[contains(text(),'客户信息')]/../p[@class='review']
        ele = wait.until(lambda x: driver.find_element(By.XPATH, "//h4[contains(text(),'客户信息')]"))
        driver.execute_script("arguments[0].scrollIntoView();", ele)    # 滚动到元素可见
        # if wait.until(lambda x: driver.find_element(By.CLASS_NAME, "review")) and is_element_present(driver, By.CLASS_NAME, "review"):
        if is_element_present(driver, By.XPATH, "//h4[contains(text(),'客户信息')]/../p[@class='success']")  and ("待完善信息") in driver.find_element(By.XPATH, "//h4[contains(text(),'客户信息')]/../p[@class='success']").text:
            logger.info("客户信息待完善")
            # 点击线下签署退款
            driver.find_element(By.XPATH, "//span[contains(text(),'线下签署退款')]").click()
            logger.info(f"点击线下签署退款菜单及url：{driver.current_url}")
            # print(f"线下签署退款url：{driver.current_url}")

            time.sleep(5)
            conf_data = read_config(path)
            print(conf_data['order_id'])
            # 订单号
            wait.until(lambda x: driver.find_element(By.NAME, "order_id")).clear()
            wait.until(lambda x: driver.find_element(By.NAME, "order_id")).send_keys(conf_data['order_id'])
            # 合同编号
            driver.find_element(By.NAME, "contract_num").clear()
            date_num = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            driver.find_element(By.NAME, "contract_num").send_keys(date_num)
            # 合同名
            driver.find_element(By.NAME, "contract_name").clear()
            driver.find_element(By.NAME, "contract_name").send_keys(conf_data['refund_contract'])
            # 签署时间
            driver.find_element(By.NAME, "date").click()
            wait.until(lambda x: driver.find_element(By.XPATH, "//div[contains(@id,'layui-laydate')]//span[@class='laydate-btns-now']")).click()
            # 附件
            driver.find_element(By.XPATH, "//input[@placeholder='请上传附件']/../a").click()
            time.sleep(3)

            # 将剪贴板内容设置为要粘贴的文本
            pyperclip.copy("D:\\WorkSpaces\\CRM\\res\\20240409160752826897.pdf")
            # 创建一个键盘控制器实例
            keyboard = Controller()

            # 按下Ctrl键
            keyboard.press(Key.ctrl.value)

            # 按下并释放'v'键
            keyboard.press('v')
            keyboard.release('v')

            # 释放Ctrl键
            keyboard.release(Key.ctrl.value)

            # 按下并释放Enter键
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)


            if "传成功" in wait.until(lambda x: driver.find_element(By.XPATH, "//div[@class='growl-notification__desc']")).text:
                # 保存
                driver.find_element(By.CSS_SELECTOR, "#saveBtn").click()

            # if read_config('../conf/config.yaml')['product'] == "研选量投":
            #     logger.info("研选量投合规二审通过，不需要财务审核，直接退款")
            # else:
            #     logger.info("财务退款审核，通过线下签署退款需要财务审核")
            #     finance_refund_audit(driver)
            finance_refund_audit(driver)
        else:
            logger.info("客户信息已完善，财务退款待审核")
            finance_refund_audit(driver)
    except Exception as e:
        logger.error(f"签署退款过程中发生错误: {e}", exc_info=True)
        driver.save_screenshot("../res/CRM签署退款错误{}.jpg".format(get_current_time()))
        # sys.exit()


def finance_refund_audit(driver):
    """
    财务退款审核
    :param driver:
    :return:
    """
    try:
        time.sleep(5)
        logger.info("财务退款审核")
        # 显性等待
        wait = WebDriverWait(driver, 10)
        # 点击财务退款审核
        wait.until(lambda x: driver.find_element(By.XPATH, "(//span[contains(text(),'退款订单')])[2]")).click()
        logger.info(f"退款订单url：{driver.current_url}")
        # print(f"退款订单url：{driver.current_url}")
        # 订单号查询
        query(driver, "orderid")

        ele = wait.until(lambda x: driver.find_element(By.XPATH, "//h4[contains(text(),'财务')]"))
        driver.execute_script("arguments[0].scrollIntoView();", ele)    # 滚动到元素可见
        # 判断财务是否审核
        if is_element_present(driver, By.XPATH, "//h4[contains(text(),'财务')]/../p[@class=' review ']"):
            logger.info("财务待审核")
            # 原路退还并结算,确认
            # wait.until(lambda x: driver.find_element(By.XPATH, "//botton[contains(text(),'原路退还')]")).click()
            # wait.until(lambda x: driver.find_element(By.XPATH, "//button[contains(text(),'保存')]")).click()
            # # if "操作成功" in wait.until(lambda x: driver.find_element(By.XPATH, "//div[contains(@id,'layui-layer')][last()]/div[1]")).text:
            # #     print(wait.until(lambda x: driver.find_element(By.XPATH, "//div[contains(@id,'layui-layer')][last()]")).text)
            # #     time.sleep(3)
            # #     wait.until(lambda x: driver.find_element(By.XPATH, "//button[contains(text(),'全部结算')]")).click()
            # #     wait.until(lambda x: driver.find_element(By.XPATH, "//a[contains(text(),'确认')]")).click()
            # #     if wait.until(lambda x: driver.find_element(By.XPATH, "//div[contains(@id,'layui-layer')][last()]/div[1]")).text == "操作成功":
            # #         logger.info("财务退款审核通过")
            # #         update_config('../conf/config.yaml', read_config('../conf/config.yaml'), 'order_id', None)
            # #     else:
            # #         msg = wait.until(lambda x: driver.find_element(By.XPATH, "//div[contains(@id,'layui-layer')][last()]")).text
            # #         logger.info(f"财务结算错误：{msg}")
            # # else:
            # #     msg = wait.until(lambda x: driver.find_element(By.XPATH, "//div[contains(@id,'layui-layer')][last()]")).text
            # #     logger.info(f"财务原路退回错误：{msg}

            ele = wait.until(lambda x: driver.find_elements(By.XPATH, "//botton[contains(text(),'原路退还')]"))
            count = len(ele)
            print(f"退款订单数量：。。。。。{count}")
            for i in range(count):
                print(f"第{i+1}个退款")

                # 判断是否存在补充信息
                if is_element_present(driver, By.XPATH, f"(//a[contains(text(),'补充信息')])[{i+1}]"):
                    print(f"第{i+1}个退款存在补充信息")
                    ele[i].click()
                    wait.until(lambda x: driver.find_element(By.XPATH, "//button[contains(text(),'保存')]")).click()

                    time.sleep(3)
                    # 滑动到底部
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    if is_element_present(driver, By.XPATH, "//botton[contains(text(),'补充信息')][{}]".format(i+1)):
                        logger.info(f"{i+1}财务原路退回错误")
                        driver.save_screenshot("../res/CRM{}财务退款原路退回失败{}.jpg".format(i, get_current_time()))
                    else:
                        logger.info(f"{i+1}财务已原路退回")
                        # # 滑动到底部
                        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        # wait.until(lambda x: driver.find_element(By.XPATH, "//button[contains(text(),'全部结算')]")).click()
                        # wait.until(lambda x: driver.find_element(By.XPATH, "//a[contains(text(),'确认')]")).click()
                        #
                        # time.sleep(3)
                        # # 滑动到底部
                        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        # # 判断是否结算
                        # if is_element_present(driver, By.XPATH, "//button[contains(text(),'全部结算')]"):
                        #     logger.info("结算失败")
                        #     driver.save_screenshot("../res/CRM财务退款结算失败{}.jpg".format(get_current_time()))
                        # else:
                        #     logger.info("结算完成")
                else:
                    logger.info(f"{i+1}财务已原路退回")

            time.sleep(3)
            # 滑动到底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 判断是否结算
            if is_element_present(driver, By.XPATH, "//button[contains(text(),'全部结算')]"):
                wait.until(lambda x: driver.find_element(By.XPATH, "//button[contains(text(),'全部结算')]")).click()
                wait.until(lambda x: driver.find_element(By.XPATH, "//a[contains(text(),'确认')]")).click()

            time.sleep(3)
            # 滑动到底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 判断是否结算
            if is_element_present(driver, By.XPATH, "//button[contains(text(),'全部结算')]"):
                logger.info("结算失败")
                driver.save_screenshot("../res/CRM财务退款结算失败{}.jpg".format(get_current_time()))
            else:
                logger.info("结算完成")
        else:
            logger.info("财务已退款，全部结算完成")

    except Exception as e:
        # logger.error(f"An error occurred: {e}", exc_info=True)
        logger.info(f"财务退款审核: {e}", exc_info=True)
        driver.save_screenshot("../res/CRM财务退款审核错误{}.jpg".format(get_current_time()))
        # sys.exit()