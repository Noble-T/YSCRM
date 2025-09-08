#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    :
# @Author  :
# @File    :
# @ProjectName:
import base64
import datetime
import os
import re
import sys
import time

import cv2
import pytesseract
import requests
from ruamel.yaml import YAML
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.log import logger


def get_current_time():
    """
    获取当前时间
    :return: 当前时间
    """
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def read_config(config_name):
    """
    读取配置文件
    :param config_name: YAML配置文件的路径
    :param key: 配置文件中要查询的键名
    :return: 配置文件内容
    """
    try:
        # 确认文件存在且为文件
        if not os.path.isfile(config_name):
            raise FileNotFoundError(f"文件 '{config_name}' 不存在。")

        yaml = YAML()
        with open(config_name, 'r', encoding='utf-8') as file:
            # 使用safe_load来加载YAML数据
            config_data = yaml.load(file)

        return config_data

    except FileNotFoundError as fnf_error:
        # print(f"文件未找到错误: {fnf_error}")
        logger.error(f"文件未找到错误: {fnf_error}")
        # 根据实际情况，这里可以选择返回一个空字典或抛出异常
        return {}
    except Exception as e:
        # print(f"加载YAML文件时发生错误: {e}")
        logger.error(f"加载YAML文件时发生错误: {e}")
        # 同上，根据实际情况处理异常
        return {}


# def modify_config(config_name, key, new_value):
#     """
#     修改配置文件
#     :param config_name: YAML配置文件的路径
#     :param key: 要修改的值的路径，以点号.分隔各层级键
#     :param new_value: 新值
#     :return:
#     """
#     try:
#         config_data = read_config(config_name)
#         # # 为配置数据的指定键路径设置新值
#         # config_data[key] = '{},'.format(new_value)
# 
#         for conf in config_data['annotations']:
#             conf['image_id'] = int(conf['image_id'])
# 
#         yaml = YAML()
#         # 打开../conf/config.yaml文件，以写入模式更新配置数据
#         with open('../conf/config.yaml', 'w', encoding='utf-8') as file:
#             # 将更新后的配置数据写入文件，数据格式为YAML
#             yaml.dump(config_data, file)  # 将Python中的字典或者列表转化为yaml格式的数据
#     except Exception as e:
#         print(f"修改YAML文件时发生错误: {e}")


def update_config(config_name, config_data, key, new_value):
    """
    修改配置文件
    :param config_name: YAML配置文件的路径
    :param config_data: 配置文件内容
    :param key: 要修改的值的路径，以点号.分隔各层级键
    :param new_value: 新值
    :return:
    """
    try:
        # # 确认文件存在且为文件
        # if not os.path.isfile(config_name):
        #     raise FileNotFoundError(f"文件 '{config_name}' 不存在。")
        # # 类型检查
        # if not isinstance(config_data, (dict, list)):
        #     raise TypeError("输入类型错误，必须是字典或列表")
        if isinstance(config_data, dict):  # 如果是字典
            for k in config_data:
                if k == key:  # 直接使用 k == key 替换 key in config_data.keys()
                    config_data[k] = new_value
                # 递归调用，优化了重复代码的部分
                update_config(config_name, config_data[k], key, new_value)
        elif isinstance(config_data, list):  # 如果是列表
            for idx, element in enumerate(config_data):
                # 递归调用，优化了重复代码的部分
                update_config(config_name, element, key, new_value)
                # 更新元素，如果需要直接在列表中更新元素
                config_data[idx] = element
        yaml = YAML()
        # 打开../conf/config.yaml文件，以写入模式更新配置数据
        with open(config_name, 'w', encoding='utf-8') as file:
            # 将更新后的配置数据写入文件，数据格式为YAML
            yaml.dump(config_data, file)  # 将Python中的字典或者列表转化为yaml格式的数据
    except Exception as e:
        logger.error(f"修改YAML文件时发生错误: {e}")


# def is_element(driver, xpaths, istest=False):
#     """
#     实现判断元素是否存在
#     :param browser: 浏览器对象
#     :param xpaths: xpaths表达式
#     :param istest: 如果为True,如果元素存在返回内容将为元素文本内容
#     :return: 是否存在
#     """
#     try:
#         target = driver.find_element_by_xpath(xpaths)
#     except exceptions.NoSuchElementException:
#         return False
#     else:
#         if istest:
#             return target.text
#         return True
def is_element_present(driver, by, value):
    """
    判断指定元素是否存在于当前页面。

    :param driver: Selenium WebDriver实例。
    :param by: 元素定位策略，如By.XPATH、By.CSS_SELECTOR等。
    :param value: 对应定位策略的值，如XPath表达式或CSS选择器。
    :return: 如果元素存在，返回True；否则返回False。
    """
    try:
        driver.find_element(by=by, value=value)
        return True
    except exceptions.NoSuchElementException:
        return False


def save_base64_image(base64_data, save_path):
    """
    将Base64编码的图片数据保存为本地图片文件。

    参数:
    base64_data (str): Base64编码的图片数据。
    save_path (str): 图片保存到本地的完整路径（包括文件名及扩展名）。
    """
    try:
        # 前缀"data:image/<格式>;base64,"标识了图片的MIME类型和Base64编码方式
        # 需要先去除前缀，再进行解码
        if base64_data.startswith('data:image/'): # 判断是否包含前缀
            # _, data = base64_data.split('data:image/', 1) # 分割字符串，只保留后半部分
            # content_type, base64_data = data.split(';base64,', 1)
            content_type, base64_data = base64_data.split(',')
        else:
            content_type = None

        # 解码Base64数据为字节串
        img_data = base64.b64decode(base64_data)

        # 根据Content-Type（如果有）推断文件扩展名，如果没有则使用默认的".png"
        ext = '.png'
        if content_type:
            mime_type, _ = content_type.split('/', 1)
            if mime_type == 'image/jpeg':
                ext = '.jpg'
            elif mime_type == 'image/gif':
                ext = '.gif'

        # 保存图片到指定路径
        with open(save_path + ext, 'wb') as f:
            f.write(img_data)
    except Exception as e:
        logger.error(f"保存图片时发生错误: {e}")
        sys.exit()


# def get_image(url, xpath_expr):
#     """
#     获取指定URL网页中符合XPath表达式的img标签的src属性，并下载图片。
#
#     参数:
#     url (str): 目标网页的URL。
#     xpath_expr (str): 用于定位img标签的XPath表达式。
#     """
#     try:
#         # 发起HTTP GET请求获取网页内容
#         response = requests.get(url)
#         response.raise_for_status()  # 如果状态码不是200，抛出异常
#         print("response.status_code：", response.status_code)
#
#         # 使用BeautifulSoup解析HTML
#         soup = BeautifulSoup(response.text, 'html.parser')
#         print("soup：", soup)
#
#         # 使用lxml库执行XPath表达式（需要先安装lxml库）
#         tree = html.fromstring(str(soup))
#         print("tree：", tree)
#         img_tags = tree.xpath(xpath_expr)
#         print("img_tags：", img_tags)
#
#         for img in img_tags:
#             src = img.get('src')
#             print("src1111：", src)
#             if src:
#                 # 下载图片
#                 download_image(src)
#     except Exception as e:
#         logger.error(f"获取图片时发生错误: {e}")
#         sys.exit()
#
#
# def download_image(url):
#     """
#     下载指定URL的图片并保存到本地。
#
#     参数:
#     url (str): 图片的URL。
#     save_path (str, optional): 保存图片的本地路径（包括文件名）。如果不提供，将使用URL最后一部分作为文件名。
#     """
#     try:
#         response = requests.get(url, stream=True)
#         # if response.status_code == 200:
#         #     if save_path is None:
#         #         save_path = url.split('/')[-1]
#
#         with open("D:\\WorkSpaces\\CRM\\res\\verify.png", 'wb') as f:
#             f.write(response.content)
#         # else:
#         #     print(f"Failed to download image. HTTP status code: {response.status_code}")
#     except Exception as e:
#         logger.error(f"下载图片时发生错误: {e}")
#         sys.exit()

# def download_image(url, save_path):
#     """
#     使用requests库下载并保存图片到指定路径。
#
#     参数:
#     url (str): 图片的URL地址。
#     save_path (str): 图片保存到本地的完整路径（包括文件名）。
#     """
#     try:
#         response = requests.get(url, stream=True)
#         with open(save_path, 'wb') as out_file:
#             out_file.write(requests.get(url).content)
#         # with open("D:\\WorkSpaces\\CRM\\res\\verify.png", 'wb') as out_file:
#         #     out_file.write(response.content)
#
#     # for img in srcObj:
#     #     with open("D:\\Images\\"+os.path.basename(img),'wb') as f:
#     #         f.write(requests.get(img).content)
#     #     print(os.path.basename(img)+"保存成功")
#     except Exception as e:
#         logger.error(f"下载图片时发生错误: {e}")
#         sys.exit()


def captcha(captcha_image_path):
    """
    识别英文、数字验证码图片中的文字
    :param captcha_image_path: 验证码图片路径
    :return: 识别出的英文数字字符串
    """
    try:
        # 读取验证码图片
        img = cv2.imread(captcha_image_path)

        # 预处理图片
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        blur = cv2.GaussianBlur(gray, (3, 3), 0)  # 应用高斯模糊

        # 可选：尝试其他预处理方法，如阈值化
        # _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 使用pytesseract进行文字识别，配置针对英文识别
        captcha_text = pytesseract.image_to_string(blur, config='--psm 6') # 使用高斯模糊和Otsu阈值化
        print("验证码：", captcha_text)

        captcha_text = re.findall(r'[A-Za-z0-9]+', captcha_text)     # 使用正则表达式匹配英文字母和数字
        return ''.join(captcha_text)    # 将匹配结果连接成一个字符串

    except Exception as e:
        logger.error(f"识别验证码时发生错误: {e}")
        sys.exit()


def img_code():
    """
    识别验证码
    :return: 验证码识别结果
    """
    try:
        # 识别验证码
        # # 获取验证码图片
        # img = driver.find_element(By.XPATH, '//*[@id="captcha"]/div[1]/img')
        # # 获取验证码图片的base64编码
        # img_base64 = img.get_attribute("src")
        # # 将base64编码转换为图片
        # img_data = base64.b64decode(img_base64.split(",")[1])
        # with open("../res/verify.png", "wb") as f:
        #     f.write(img_data)

        # 通过第三方接口发送请求识别验证码图片内容
        url2 = "https://upload.chaojiying.net/Upload/Processing.php"
        # 传参数据
        data = {
            # 用户名
            "user": "tianqiu2",
            # 密码
            "pass": "ltqiu123456",
            # 用户id
            "sofid": "949627",
            # 验证码的编号:整数类型
            "codetype": 1902
        }
        # 提取验证码图片
        files = {"userfile": open("../res/verify.png", "rb")}
        # 发送请求识别验证码
        resp = requests.post(url2, data=data, files=files)
        # 查看响应结果
        # print(type(resp.json())) # <class 'dict'>返回结果是字典类型
        # print(resp.json())
        res = resp.json()
        print(res)
        # 提取验证码数字
        if res["err_no"] == 0:
            code = res["pic_str"]
            print(f"验证码识别成功：{code}")
            return code
        else:
            print("验证码识别失败")
            return False
    except Exception as e:
        logger.error(f"第三方接口识别验证码图片发生错误: {e}", exc_info=True)


# 定义登录流程
def login(driver):
    """
    登录流程
    :param driver: 浏览器对象
    :return:
    """
    try:
        config_data = read_config('../conf/config.yaml')
        # cmr后台URL
        url = config_data['crm']['url']
        driver.get(url)

        driver.add_cookie({
            "name": config_data['crm']['cookie']['name'],
            "value": config_data['crm']['cookie']['value']
        })
        driver.get(url)
        time.sleep(3)

        # 显式等待
        wait = WebDriverWait(driver, 10)
        if is_login_success(driver) is False:
            # 找到并点击账号登录按钮
            # element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.login_wrapper > div.dingTalk > span.switch_login.pointer")))
            element = wait.until(lambda x: driver.find_element(By.CSS_SELECTOR, "div.login_wrapper > div.dingTalk > span.switch_login.pointer"))
            driver.execute_script('arguments[0].click()', element)
            # while True
            for i in range(1, 6): # 循环5次
                print(f"\n第{i}次登录")
                logger.info(f"第{i}次账号密码登录")
                # 输入账号和密码
                driver.find_element(By.CSS_SELECTOR, "li.username > label > input").clear()
                driver.find_element(By.CSS_SELECTOR, "li.username > label > input").send_keys(config_data['crm']['username'])
                driver.find_element(By.CSS_SELECTOR, "li.password > label > input").clear()
                driver.find_element(By.CSS_SELECTOR, "li.password > label > input").send_keys(config_data['crm']['password'])
                print("输入账号和密码完成")

                # 判断验证码是否存在
                if is_element_present(driver, By.XPATH,"//li[@class='verify']//img"):
                    print("验证码存在")
                    # 点击刷新验证码
                    driver.find_element(By.XPATH, "//*[@class='verify']//img").click()
                    # 截取验证码图片
                    driver.find_element(By.XPATH, "//*[@class='verify']//img").screenshot("../res/verify.png")
                    # # 获取"//*[@class='verify']//img" src属性
                    # src = driver.find_element(By.XPATH, "//li[@class='verify']//img").get_attribute("src")
                    # print("src：", src)
                    # # src = driver.find_element(By.XPATH, "//*[@class='verify']//img").get("src") # 获取验证码图片的base64编码
                    #
                    # save_base64_image(src, "D:\\WorkSpaces\\CRM\\res\\verify")

                    # 调用识别验证码函数获取验证码内容
                    code = captcha("../res/verify.png")
                    print(f"验证码识别结果：{code}")
                    # 输入验证码
                    driver.find_element(By.CSS_SELECTOR, "li.verify > label.inline-block.relative.label-required-null.label-required-prev > input").clear()
                    driver.find_element(By.CSS_SELECTOR, "li.verify > label.inline-block.relative.label-required-null.label-required-prev > input").send_keys(code)
                    time.sleep(3)

                # 点击登录按钮
                login_button = driver.find_element(By.CSS_SELECTOR, "li.text-center.padding-top-20 > button")
                login_button.click()
                time.sleep(3)
                if is_login_success(driver) is True:
                    # 更新cookie值
                    cookies = driver.get_cookies()
                    update_config('../conf/config.yaml', config_data, 'value', cookies)
                    break
                if i == 5:
                    logger.error("登录失败，请检查账号密码是否正确")
                    sys.exit()
    except Exception as e:
        logger.error(f"登录过程中发生错误: {e}", exc_info=True)
        driver.save_screenshot("../res/CRM登录错误{}.jpg".format(get_current_time()))
        # quit()
        logger.error(f"登录过程中发生错误退出程序: {e}")
        sys.exit(f"登录过程中发生错误退出程序: {e}")


# 是否登录成功
def is_login_success(driver):
    """
    判断是否登录成功
    :param driver: 浏览器对象
    :return:
    """
    time.sleep(5)
    wait = WebDriverWait(driver, 10)

    # 判断是否登录成功
    if "系统管理后台" in wait.until(lambda x: driver.title):
        logger.info("登录成功")
        return True
    else:
        logger.info("登录失败")
        # print("登录失败，正在重试")
        driver.save_screenshot("../res/CRM登录失败{}.jpg".format(get_current_time()))
        return False


# # 登录并转到工作台V2
# def navigate_to_workbench_v2(driver):
#     """
#     登录并转到工作台V2
#     :param driver: 浏览器对象
#     :return:
#     """
#     try:
#         # 显式等待
#         wait = WebDriverWait(driver, 10)
#         element_li = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.layui-header.notselect > ul.layui-nav.layui-layout-left > li:nth-child(4) a > span")))
#         driver.execute_script('arguments[0].click()', element_li)
#         print("点击工作台V2：")
#     except Exception as e:
#         logger.error(f"跳转到工作台V2发生错误: {e}", exc_info=True)


# 查询
def query(driver, query_type):
    """
    查询流程
    :param query_type: name=姓名查询，orderid=订单号查询
    :param driver: 浏览器对象
    :return:
    """
    try:
        wait = WebDriverWait(driver,10)
        config_datas = read_config('../conf/config.yaml')
        if query_type == "name":
            # 输入姓名查询
            # ele = wait.until(lambda x: driver.find_element(By.XPATH, "//input[@placeholder='请输入客户昵称或备注']"))
            ele = wait.until(lambda x: driver.find_element(By.NAME, "name"))
            ele.send_keys(config_datas['crm']['name'])
            logger.info(f"输入姓名查询：{config_datas['crm']['name']}")
        if query_type == "orderid":
            # 输入订单号查询
            # ele = wait.until(lambda x: driver.find_element(By.XPATH, "//input[@placeholder='请输入订单号']"))
            ele = wait.until(lambda x: driver.find_element(By.NAME, "order_id"))
            ele.clear()
            ele.send_keys(config_datas['order_id'])
            logger.info(f"输入订单号查询：{config_datas['order_id']}")

        # 点击搜索
        ele = wait.until(lambda x: driver.find_element(By.XPATH, "//button[@class='layui-btn layui-btn-primary'][1]"))
        ele.click()

        # 核对手机号
        # //td[contains(text(),'赵楠')]/following-sibling::td[1]

        # 点击详情
        time.sleep(5)
        ele = wait.until(lambda x: driver.find_element(By.XPATH, "//a[contains(text(),'详情')]/.."))
        ele.click()
        logger.info("进入详情")

    except Exception as e:
        logger.error(f"查询过程中发生错误: {e}", exc_info=True)
        driver.save_screenshot("../res/CRM查询错误{}.jpg".format(get_current_time()))
        # sys.exit()


def delete_files(directory, pattern):
    """
    删除指定目录下文件名中包含特定模式的所有文件。

    :param directory: 要搜索的目录路径
    :param pattern: 文件名中要匹配的模式
    """
    # 编译正则表达式
    regex = re.compile(pattern)

    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件名是否匹配模式
            if regex.search(file):
                file_path = os.path.join(root, file)
                print(f"Deleting: {file_path}")
                os.remove(file_path)
