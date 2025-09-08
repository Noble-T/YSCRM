#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/4/8 10:41
@Author  :
@File    : main_crm.py
@ProjectName: CRM
'''


from selenium import webdriver
from utils.log import logger
from utils.utils import login, delete_files
from test_case.nav_workbench_v2 import navigate_to_workbench_v2, compliance_files

if __name__ == "__main__":
    logger.info("Program started.")
    # 删除指定目录下文件名中包含特定模式的所有文件。
    delete_files("D:\\WorkSpaces\\CRM\\res", r"CRM")

    # 配置浏览器选项，允许页面在后台运行而不自动关闭
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)

    # 创建Chrome浏览器实例
    driver = webdriver.Chrome()
    # 将窗口最大化
    driver.maximize_window()

    # 主程序逻辑
    login(driver)
    navigate_to_workbench_v2(driver)
    compliance_files(driver)

    input("Press Enter to exit...")

    driver.quit()
    logger.info("Program exited.")
