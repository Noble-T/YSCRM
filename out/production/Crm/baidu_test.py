#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    :
# @Author  :
# @File    :
# @ProjectName:
# import time
# from selenium import webdriver
# # 创建驱动对象
# driver = webdriver.Chrome()
# # 访问被测地址
# url = "https://www.baidu.com/"
# driver.get(url)
# # 页面最大化
# driver.maximize_window()
# # 强制等待
# time.sleep(5)
# # 关闭驱动
# driver.quit()

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# # 不自动关闭浏览器
# option = webdriver.ChromeOptions()
# option.add_experimental_option("detach", True)
# # 创建驱动对象
# driver = webdriver.Chrome(options=option)
# # 访问被测地址
# url = "https://pay.oneil88.com/admin"
# driver.get(url)
# # 页面最大化
# driver.maximize_window()
# # 显式等待
# wait = WebDriverWait(driver, 10)
# element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.login_wrapper > div.dingTalk > span.switch_login.pointer")))
# # 点击账号登录
# driver.find_element(By.CSS_SELECTOR, "div.login_wrapper > div.dingTalk > span.switch_login.pointer").click()
# # 输入账号
# driver.find_element(By.CSS_SELECTOR, "li.username > label > input").send_keys("admin")
# # 输入密码
# driver.find_element(By.CSS_SELECTOR, "li.password > label > input").send_keys("123456")
# # 点击登录
# driver.find_element(By.CSS_SELECTOR, "li.text-center.padding-top-20 > button").click()
#
# # 点击工作台V2
# element_li = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.layui-header.notselect > ul.layui-nav.layui-layout-left > li:nth-child(4)")))
# driver.find_element(By.CSS_SELECTOR, "div.layui-header.notselect > ul.layui-nav.layui-layout-left > li:nth-child(4)").click()
# input("点击工作台V2：")
#
# # 关闭驱动
# driver.quit()

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.utils import read_config

# 配置浏览器选项，允许页面在后台运行而不自动关闭
option = webdriver.ChromeOptions()
option.add_experimental_option("detach", True)

# 创建Chrome浏览器实例
driver = webdriver.Chrome(options=option)

# 将窗口最大化
driver.maximize_window()

# # 访问目标URL
# url = "https://pay.oneil88.com/admin"
# driver.get(url)
#
#
#
# driver.add_cookie({
#     "name": "jmftou",
#     "value": "a4152224628ba20e86799f7544cafa1c"
# })
# driver.get(url)

config_data = read_config('config.yaml')
# cmr后台URL
url = config_data['crm']['url']
driver.get(url)

driver.add_cookie({
    "name": config_data['crm']['cookie']['name'],
    "value": config_data['crm']['cookie']['value']
})
driver.get(url)


def is_exists(driver, element):
    """
    基本实现判断元素是否存在
    :param driver: 浏览器对象
    :param element: element表达式
    :return: 是否存在
    """
    try:
        driver.find_element(By.XPATH, element)
        return True
    except exceptions.NoSuchElementException:
        return False


# 显式等待
wait = WebDriverWait(driver, 10)


# # 登录流程
# def login():
#     # print(len(driver.find_elements(By.XPATH, "//*[@id='s-top-loginbt']")))
#     if is_exists(driver, "//*[@id='s-top-loginbtn']"):
#         print("元素存在，点击账号登录按钮：")
#         # 找到并点击账号登录按钮
#         element = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='s-top-loginbtn']")))
#         driver.execute_script('arguments[0].click()', element)
#
#     # 输入账号和密码
#     # sleep(15)
#     driver.find_element(By.CSS_SELECTOR, "li.username > label > input").send_keys("admin")
#     driver.find_element(By.CSS_SELECTOR, "li.password > label > input").send_keys("123456")
#
#     # 点击登录按钮
#     login_button = driver.find_element(By.CSS_SELECTOR, "li.text-center.padding-top-20 > button")
#     login_button.click()


# 登录并转到工作台V2
def navigate_to_workbench_v2():
    element_li = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.layui-header.notselect > ul.layui-nav.layui-layout-left > li:nth-child(4) a > span")))
    driver.execute_script('arguments[0].click()', element_li)
    print("点击工作台V2：")

    # driver.switch_to.window(driver.window_handles[-1]) # 切换到最新打开的窗口
    ele = wait.until(lambda x: driver.find_element(By.XPATH, "(//span[contains(text(),'合规档案')])[2]"))
    driver.execute_script("arguments[0].scrollIntoView();", ele)    # 滚动到元素可见
    ele.click()

# 主程序逻辑
try:
    # login()
    navigate_to_workbench_v2()
except Exception as e:
    print(f"An error occurred: {e}")
    # 可在此添加错误处理逻辑，例如记录日志、重试或通知用户

input("Press Enter to exit...")
# 关闭浏览器驱动
driver.quit()
