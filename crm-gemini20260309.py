#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2026/3/9 17:53 
@Author  : 
@File    : crm-gemini20260309.py
@ProjectName: CRM 
@Description:
你是资深测开工程师，我需要模拟用户登录crm，登录页面，有验证码，验证码图片从/html/body/div[2]/div[2]/div[2]/form/ul/li[3]/label[2]/img中提取。使用 ddddocr 库，符合实际工作使用的企业级项目  
 
<img alt="img" src="data:image/png;base64,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">

你好！我是 Gemini。作为一个在企业级自动化测试领域“摸爬滚打”过的 AI，我非常理解处理验证码时的那种“既想保证自动化率，又不想破坏测试环境纯净度”的纠结。

针对你的需求，使用 dddddocr（带带弟弟 OCR）是一个非常实用的选择，它不需要安装复杂的 Tesseract 或连接外部付费 API。

🛠️ 核心思路
浏览器驱动：使用 Selenium 获取页面元素。

验证码提取：不推荐通过 URL 二次下载（可能导致验证码刷新），建议直接通过 Canvas 或 Base64 截图 方式获取当前显示的图片数据。

识别：使用 dddddocr 处理二进制流。

工程化：将登录逻辑封装为类，增加重试机制（毕竟 OCR 识别率不是 100%）。

💻 企业级项目代码实现



资深测开的避坑指南（企业级 Tips）
关于 screenshot_as_png：
这是最稳妥的方法。不要试图用 requests 去下载图片地址，因为验证码通常是和 Session 绑定的，且很多后端逻辑是“一请求一刷新”，二次下载拿到的验证码和页面显示的绝对不一样。

元素定位稳定性：
你提供的 XPath 比较“深”（绝对路径）。在企业项目中，这种路径极易随前端改版而失效。建议联系前端加上 id="captcha_img"，或者使用相对路径如 //form//img[contains(@src, 'data:image')]。

Ddddocr 的依赖：
确保你安装了最新的库：pip install ddddocr。注意，如果是在 Linux 容器（Docker）中运行，可能需要安装额外的图形库依赖（如 libsm6, libxext6）。

Base64 处理：
如果你的验证码图片是直接写在 HTML 里的 Base64 字符串（就像你给出的示例代码），你也可以通过 get_attribute('src') 拿到字符串，去掉 data:image/png;base64, 前缀后用 base64.b64decode() 解码，再交给 OCR。



资深测开的额外建议：
关于 XPath 定位：
你提供的 /html/body/div[2]/div[2]/div[2]/form/ul/li[3]/label[2]/img 是“绝对路径”，非常脆弱。

建议： 使用 //form//li[contains(., "验证码")]//img 这种带逻辑语义的定位方式，即便 UI 改版（比如多套了一个 div），脚本依然能精准找到。

Base64 图片处理：
在你给出的 HTML 片段中，src 是 data:image/png;base64,...。这意味着图片不需要联网下载。我的代码中 get_captcha_image_bytes 已经兼容了这种模式，直接截取内存数据，速度飞快。

失败判定：
如果登录失败（验证码错），CRM 页面通常会弹窗提示。在生产脚本中，最好加一个判断：if "验证码错误" in self.driver.page_source: ...，这样能更精准地触发重试。

接下来的步骤：
你需要把代码里的 By.CSS_SELECTOR 定位符替换成你 CRM 真实的 id 或 name。



'''
import base64
import time
import ddddocr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CRMLoginMaster:
    def __init__(self, headless=False):
        # 1. 初始化 OCR (设置不显示广告，避免日志污染)
        self.ocr = ddddocr.DdddOcr(show_ad=False)

        # 2. 配置浏览器
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def get_captcha_image_bytes(self, xpath):
        """
        核心逻辑：提取验证码图片字节流
        适配两种情况：1. 直接是 Base64 源码  2. 普通图片链接
        """
        try:
            img_element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            src = img_element.get_attribute("src")

            if src and "base64," in src:
                # 情况 A: 图片数据就在 HTML 里 (src="data:image/png;base64,xxxx")
                base64_str = src.split("base64,")[1]
                return base64.b64decode(base64_str)
            else:
                # 情况 B: 这是一个 URL 图片，直接截取元素图，防止二次请求刷新
                return img_element.screenshot_as_png
        except Exception as e:
            print(f"❌ 验证码元素提取失败: {e}")
            return None

    def check_login_status(self):
        """
        判定是否登录成功：根据 URL 变化或特定 Dashboard 元素出现
        """
        try:
            # 假设登录成功后 URL 包含 'index' 或 'dashboard'
            self.wait.until(lambda d: "login" not in d.current_url or "index" in d.current_url)
            return True
        except TimeoutException:
            return False

    def login(self, url, user, pwd, max_retries=5):
        """
        带重试机制的登录主流程
        """
        self.driver.get(url)

        # 优化后的相对路径定位（比你给的长路径更健壮）
        # 建议根据实际情况微调这些 ID 或 Name
        captcha_img_xpath = "//form//img[contains(@src, 'data:image') or contains(@alt, 'img')]"

        for attempt in range(max_retries):
            print(f"🔄 正在尝试登录 (第 {attempt + 1}/{max_retries} 次)...")

            try:
                # 1. 识别验证码
                img_bytes = self.get_captcha_image_bytes(captcha_img_xpath)
                if not img_bytes:
                    self.driver.refresh()
                    continue

                captcha_code = self.ocr.classification(img_bytes)
                print(f"💡 OCR 识别结果: {captcha_code}")

                # 2. 填写表单 (请根据 CRM 实际 ID 修改定位符)
                self.driver.find_element(By.XPATH, "//form//input[contains(@placeholder, '登录账号')]").clear()
                self.driver.find_element(By.XPATH, "//form//input[contains(@placeholder, '登录账号')]").send_keys(user)

                self.driver.find_element(By.XPATH, "//form//input[contains(@placeholder, '登录密码')]").clear()
                self.driver.find_element(By.XPATH, "//form//input[contains(@placeholder, '登录密码')]").send_keys(pwd)

                # 找到验证码输入框并输入
                # 这里通常在图片旁边的 li[3] 下面
                captcha_input = self.driver.find_element(By.XPATH, "//input[contains(@placeholder, '验证码')]")
                captcha_input.clear()
                captcha_input.send_keys(captcha_code)

                # 3. 提交登录
                self.driver.find_element(By.XPATH, "//button | //input[@type='submit']").click()

                # 4. 验证结果
                time.sleep(2) # 等待后端响应
                if self.check_login_status():
                    print("✅ CRM 登录成功！")
                    return True
                else:
                    print("⚠️ 验证码错误或登录超时，刷新重试...")
                    # 登录失败通常需要点击图片刷新，或者直接刷新页面
                    self.driver.refresh()

            except Exception as e:
                print(f"⚠️ 当前轮次发生错误: {e}")
                self.driver.refresh()

        return False

    def close(self):
        self.driver.quit()

# --- 运行入口 ---
if __name__ == "__main__":
    # 企业级项目通常从环境变量或配置文件读取凭据
    CRM_URL = "https://crm.abctougu.cn/admin/login.html"
    USER = "admin"
    PASS = "I~~Jjq\-MW4orea\14"

    crm = CRMLoginMaster(headless=False)
    try:
        if crm.login(CRM_URL, USER, PASS):
            # 登录成功后的业务操作...
            print("开始执行后续测试用例...")
        else:
            print("❌ 达到最大重试次数，登录失败。")
    finally:
        # crm.close() # 调试阶段可以先不关闭
        pass