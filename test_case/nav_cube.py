#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2025/3/28 17:27 
@Author  : 
@File    : nav_cube.py
@ProjectName: CRM 
'''
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.log import logger
from utils.utils import get_current_time, is_element_present


def navigate_to_cube(driver):
    """
    跳转到天眼魔方
    :param driver:
    :return:
    """
    try:
        # 显式等待
        wait = WebDriverWait(driver, 10)
        ele = wait.until(EC.visibility_of_element_located((By.XPATH, "(//span[contains(text(),'天眼魔方')])")))
        driver.execute_script('arguments[0].click()', ele)
        logger.info("点击天眼魔方")
    except Exception as e:
        logger.error("点击天眼魔方失败" + str(e))
        driver.save_screenshot("../res/CRM点击天眼魔方失败{}.jpg".format(get_current_time()))
        raise e


def menu_learning(driver):
    """
    Learning菜单
    :param driver:
    :return:
    """
    try:
        # 显式等待
        wait = WebDriverWait(driver, 10)
        ele = wait.until(EC.visibility_of_element_located((By.XPATH, "(//span[contains(text(),'Learning')])")))
        driver.execute_script("arguments[0].scrollIntoView();", ele)    # 滚动到元素可见
        ele.click()
        logger.info("点击学习")
    except Exception as e:
        logger.error("点击学习失败" + str(e))
        driver.save_screenshot("../res/CRM点击学习失败{}.jpg".format(get_current_time()))
        raise e


# 章节训练
def chapter_training(driver):
    """
    章节训练
    :param driver:
    :return:
    """
    try:
        # 显式等待
        wait = WebDriverWait(driver, 10)
        eles = "(//a[contains(text(),'章节训练')])"
        count = len(eles)
        if is_element_present(driver, By.XPATH, eles):
            for i in range(count): # 任务训练
                ele = wait.until(EC.visibility_of_element_located((By.XPATH, f"{eles[i]}/../following-sibling::span")))
                if ele.text == "今日未完成":
                    eles[i].click()
                    logger.info(f"点击章节训练：{eles[i].text}")
                    tables= wait.until(EC.visibility_of_element_located((By.XPATH, "//ul[contains(@class,'layui-tab-title')]/li")))
                    count_table = len(tables)
                    for j in range(count_table): # 章节类型
                        butons = "//a[contains(text(),'做题')]"
                        count_button = len(butons)
                        if is_element_present(driver, By.XPATH, butons):
                            for k in range(count_button): # 做题
                                butons[k].click()
                                if is_element_present(driver, By.XPATH, "//button[contains(text(),'提交')]"):
                                    logger.info("做题成功")
                                    break
                                else:
                                    logger.info("做题失败")
                            break
                        else:
                            if j < count_table - 1:
                                tables[j+1].click()
                                logger.info(f"点击章节训练：{tables[j+1].text}")
                            else:
                                logger.info("章节全部训练")
                            return

                    break
        else:
            logger.info("没有章节训练")
            return


        eles = "(//span[contains(text(),'章节训练')])[{}]".format(count)
        ele = wait.until(EC.visibility_of_element_located((By.XPATH, eles)))
        driver.execute_script("arguments[0].scrollIntoView();", ele)    # 滚动到元素可见
        ele.click()
        logger.info("点击章节训练")
    except Exception as e:
        logger.error("点击章节训练失败"+ str(e))
        driver.save_screenshot("../res/CRM点击章节训练失败{}.jpg".format(get_current_time()))
        raise e