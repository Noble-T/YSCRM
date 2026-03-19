#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2026/3/17 17:51 
@Author  : 
@File    : user_search.py
@ProjectName: CRM 
@Description: 
'''
import requests
from time import sleep

# =======================
# 配置区
# =======================

BASE_URL = "https://crm.blzt888.com/crm_v2/system.user_search/index.html"

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

# cookie配置
COOKIES = {
    "jmftou": "003701fb978b67f42cf862a117d855dc"
}
# 请求间隔（秒），避免接口频繁调用被封
REQUEST_INTERVAL = 1
# 请求次数
REQUEST_COUNT = 22

# =======================
# 函数模块区
# =======================

def build_params(mobile, app_userid="", unionid=""):
    """
    构建接口请求参数
    :param mobile: 手机号
    :param app_userid: 用户ID（可选）
    :param unionid: unionid（可选）
    :return: dict格式参数
    """
    return {
        "mobile": str(mobile),
        "app_userid": app_userid,
        "unionid": unionid
    }

def send_request(url, params, cookies):
    """
    发送GET请求
    :param url: 接口地址
    :param params: 请求参数
    :param cookies: 请求Cookie
    :return: 响应JSON或文本
    """
    try:
        response = requests.get(url, params=params, cookies=cookies, timeout=10)
        response.raise_for_status()  # 如果状态码不是200，会抛出异常
        # 尝试返回JSON，如果失败返回文本
        try:
            return response, response.json()
        except ValueError:
            return response, response.text
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None, None

def main():
    """
    主函数：循环发送请求，mobile自增，并将结果存入列表
    """
    # 初始手机号
    mobile = 13000000001
    results = []  # 用于存储所有接口返回结果
    for i in range(REQUEST_COUNT):
        print(f"第 {i+1} 次请求, mobile={mobile}")
        params = build_params(mobile)
        response, result = send_request(BASE_URL, params, COOKIES)
        # 响应时间, 单位毫秒
        request_time = response.elapsed.total_seconds()
        print(f"响应时间：{request_time:.2f} 秒")

        # 输出状态码
        if response:
            print(f"响应状态码：{response.status_code}")

            # 检查响应结果是否包含"20 次"，如果包含则退出
            if result and isinstance(result, dict): # 尝试判断结果是否为字典
                result_str = str(result)
                if "20次" in result_str:
                    print("⚠️  检测到查询次数限制（20 次），程序退出")
                    break
        else:
            print("请求失败，无状态码")

        results.append({"i": i+1, "mobile": mobile, "response_code": response.status_code, "response_time": response.elapsed.total_seconds(), "result": result})
        mobile += 1  # mobile自增
        sleep(REQUEST_INTERVAL)  # 等待，避免过快请求

    # 最终统一打印列表
    print("\n所有接口请求结果列表：")
    for item in results:
        print(item)

# =======================
# 脚本入口
# =======================
if __name__ == "__main__":
    main()




# import requests
# import json
# import time
#
# # ==========================================
# # 配置模块
# # ==========================================
# class Config:
#     BASE_URL = "https://crm.blzt888.com/crm_v2/system.user_search/index.html"
#     HEADERS = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#         "Cookie": "jmftou=003701fb978b67f42cf862a117d855dc",
#         "Accept": "application/json, text/javascript, */*; q=0.01" # 明确期望返回格式
#     }
#
# # ==========================================
# # 业务逻辑模块
# # ==========================================
# class CRMUserSearcher:
#     def __init__(self):
#         self.session = requests.Session()
#         self.session.headers.update(Config.HEADERS)
#
#     def search_user(self, mobile_number):
#         """
#         执行用户搜索并处理返回结果
#         :param mobile_number: 手机号
#         :return: (bool, dict/str) -> (是否成功, 返回的内容)
#         """
#         params = {
#             "spm": "m-204-254-411",
#             "mobile": mobile_number,
#             "app_userid": "",
#             "unionid": ""
#         }
#
#         try:
#             response = self.session.get(Config.BASE_URL, params=params, timeout=10)
#
#             # 1. 检查 HTTP 状态码
#             if response.status_code != 200:
#                 return False, f"HTTP Error: {response.status_code}"
#
#             # 2. 尝试解析为 JSON，如果不是 JSON 则返回文本内容
#             try:
#                 result_data = response.json()
#                 return True, result_data
#             except json.JSONDecodeError:
#                 return True, response.text[:100] # 只取前100字符防止刷屏
#
#         except requests.exceptions.RequestException as e:
#             return False, str(e)
#
# # ==========================================
# # 测试流程控制模块
# # ==========================================
# def run_api_test_suite(start_mobile, iterations):
#     """
#     运行测试套件并打印格式化的结果
#     """
#     searcher = CRMUserSearcher()
#     print(f"{'序号':<5} | {'手机号':<12} | {'状态':<6} | {'返回结果摘要'}")
#     print("-" * 60)
#
#     for i in range(iterations):
#         current_mobile = str(start_mobile + i)
#
#         # 执行请求
#         is_ok, content = searcher.search_user(current_mobile)
#
#         # 格式化输出
#         status_str = "SUCCESS" if is_ok else "FAILED"
#
#         # 模拟简单的断言：假设返回结果中包含 'code' 字段且为 1 代表业务成功
#         # if isinstance(content, dict) and content.get('code') == 1:
#         #     status_str = "PASS"
#
#         print(f"{i+1:<5} | {current_mobile:<12} | {status_str:<6} | {content}")
#
#         # 控制请求频率
#         time.sleep(1)
#
# # ==========================================
# # 主程序入口
# # ==========================================
# if __name__ == "__main__":
#     # 配置初始参数
#     START_NUMBER = 13000000001
#     TOTAL_TESTS = 25  # 测试10个自增手机号
#
#     run_api_test_suite(START_NUMBER, TOTAL_TESTS)






# """
# ==================================================
# CRM 用户搜索接口自动化测试脚本
# ==================================================
# 功能说明：
# 1. 接口地址与请求参数完全分离
# 2. mobile 从 13000000000 开始自增（可配置步长和次数）
# 3. 固定 Cookie: kour=343245ertwedf5w52152
# 4. 结构清晰、模块化、注释完整，适合团队协作
# 5. 可直接运行（无需修改即可执行）
#
# 作者：Grok（根据用户需求生成）
# 版本：1.0
# 日期：2026-03-19
# 使用方法：
#     python crm_user_search_test.py
# """
#
# import requests
# from typing import Dict, Any
# import time
#
#
# # =============================================
# # 1. 配置模块（所有常量集中管理，便于维护）
# # =============================================
# class Config:
#     """全局配置类 - 所有可配置项都在这里，便于团队统一修改"""
#
#     # 接口地址（不带任何参数）
#     BASE_URL = "https://crm.blzt888.com/crm_v2/system.user_search/index.html"
#
#     # 默认请求参数（mobile 会动态覆盖）
#     DEFAULT_PARAMS: Dict[str, str] = {
#         "spm": "m-204-254-411",
#         "app_userid": "",
#         "unionid": ""
#     }
#
#     # Cookie（完全按照用户要求）
#     COOKIES: Dict[str, str] = {
#         "jmftou": "003701fb978b67f42cf862a117d855dc"
#     }
#
#     # 请求头（推荐携带，防止被拦截）
#     HEADERS: Dict[str, str] = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                       "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#         "Accept-Language": "zh-CN,zh;q=0.9",
#         "Connection": "keep-alive"
#     }
#
#     # 测试参数（mobile 自增相关）
#     START_MOBILE: int = 13000000001      # 起始手机号
#     INCREMENT_STEP: int = 1              # 每次递增步长
#     NUM_TESTS: int = 22                  # 测试次数（可自行修改）
#
#     # 其他通用设置
#     TIMEOUT: int = 10                    # 请求超时秒数
#     SLEEP_INTERVAL: float = 1.5          # 每次请求间隔（防止被风控）
#
#
# # =============================================
# # 2. 工具函数模块（高度复用）
# # =============================================
# def build_request_params(mobile: int) -> Dict[str, str]:
#     """
#     构建本次请求的参数字典
#     - mobile 动态传入，实现自增
#     - 其他参数从 Config.DEFAULT_PARAMS 复制，避免污染全局配置
#     """
#     params = Config.DEFAULT_PARAMS.copy()   # 深拷贝防止引用问题
#     params["mobile"] = str(mobile)          # 必须转为字符串，符合URL规范
#     return params
#
#
# def send_request(params: Dict[str, str]) -> requests.Response:
#     """
#     统一发送 GET 请求
#     返回 Response 对象，方便后续断言和日志
#     """
#     try:
#         response = requests.get(
#             url=Config.BASE_URL,
#             params=params,
#             cookies=Config.COOKIES,
#             headers=Config.HEADERS,
#             timeout=Config.TIMEOUT,
#             allow_redirects=True
#         )
#         # 打印关键日志（便于调试）
#         print(f"✅ 请求成功 | mobile={params.get('mobile')} | 状态码={response.status_code} | "
#               f"响应大小={len(response.text)} 字符")
#         return response
#
#     except requests.exceptions.RequestException as e:
#         print(f"❌ 请求异常 | mobile={params.get('mobile')} | 错误信息={e}")
#         raise
#
#
# # =============================================
# # 3. 测试执行模块（核心业务逻辑）
# # =============================================
# def single_test_case(mobile: int) -> None:
#     """
#     单次接口测试用例
#     - 包含完整日志和简单断言示例
#     - 便于后续扩展 pytest / unittest
#     """
#     print(f"\n{'='*60}")
#     print(f"🚀 开始测试 - mobile = {mobile}")
#
#     # 1. 组装参数
#     params = build_request_params(mobile)
#
#     # 2. 发送请求
#     response = send_request(params)
#
#     # 3. 简单业务断言（可根据实际页面内容自行扩展）
#     assert response.status_code == 200, f"❌ 状态码错误: {response.status_code}"
#
#     # 示例：检查页面是否包含关键字段（实际可替换为业务关键词）
#     content = response.text.lower()
#     if "用户" in content or "search" in content or len(content) > 500:
#         print("✅ 业务校验通过（页面包含有效内容）")
#     else:
#         print("⚠️  业务校验提醒：页面内容可能为空，请人工确认")
#
#     print(f"📌 完整 URL（供复制验证）: {response.url}")
#     print(f"{'='*60}\n")
#
#
# def run_all_tests() -> None:
#     """
#     执行批量测试（mobile 自增）
#     - 循环调用 single_test_case
#     - 支持配置测试次数和间隔
#     """
#     print("🎯 ==================== 开始 CRM 用户搜索接口批量测试 ====================")
#     print(f"📍 测试范围: {Config.START_MOBILE} ~ "
#           f"{Config.START_MOBILE + (Config.NUM_TESTS-1)*Config.INCREMENT_STEP}")
#     print(f"📍 测试次数: {Config.NUM_TESTS} | 间隔: {Config.SLEEP_INTERVAL}秒\n")
#
#     start_time = time.time()
#
#     for i in range(Config.NUM_TESTS):
#         current_mobile = Config.START_MOBILE + i * Config.INCREMENT_STEP
#         single_test_case(current_mobile)
#
#         # 防止被封，请求之间加间隔
#         if i < Config.NUM_TESTS - 1:
#             time.sleep(Config.SLEEP_INTERVAL)
#
#     total_time = time.time() - start_time
#     print(f"🎉 所有测试执行完成！共 {Config.NUM_TESTS} 条用例，用时 {total_time:.2f} 秒")
#
#
# # =============================================
# # 4. 主入口（直接运行）
# # =============================================
# if __name__ == "__main__":
#     """
#     程序入口
#     - 直接运行 python 文件即可开始测试
#     - 建议团队成员在虚拟环境运行：pip install requests
#     """
#     # 可在此处快速修改测试参数（覆盖 Config 默认值）
#     # Config.NUM_TESTS = 20          # 示例：想测20条就取消注释
#
#     run_all_tests()
#
#     print("\n💡 使用提示：")
#     print("   1. 修改 Config.NUM_TESTS 可控制测试数量")
#     print("   2. 修改 Config.START_MOBILE 可更改手机号起点")
#     print("   3. 如需保存日志，可自行添加 logging 模块")
#     print("   4. 如需断言增强，欢迎继续迭代！")











# import requests
# import time
#
# # ==========================
# # 配置模块
# # ==========================
#
# # 接口基础信息
# BASE_URL = "https://crm.blzt888.com/crm_v2/system.user_search/index.html"
# HEADERS = {
#     "Cookie": "jmftou=003701fb978b67f42cf862a117d855dc",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
# }
#
# # 请求参数模板
# PARAM_TEMPLATE = {
#     "spm": "m-204-254-411",
#     "mobile": "",  # 这里会在函数中动态填充
#     "app_userid": "",
#     "unionid": ""
# }
#
# # 测试设置
# START_MOBILE = 13000000001  # 初始手机号
# REQUEST_COUNT = 5  # 请求次数，可根据需要调整
# DELAY_BETWEEN_REQUESTS = 1  # 每次请求间隔秒数
#
#
# # ==========================
# # 工具函数模块
# # ==========================
#
# def build_params(mobile_number: int) -> dict:
#     """
#     根据手机号构建请求参数
#     :param mobile_number: 当前请求的手机号
#     :return: 完整请求参数字典
#     """
#     params = PARAM_TEMPLATE.copy()
#     params["mobile"] = str(mobile_number)
#     return params
#
#
# def send_request(url: str, params: dict, headers: dict) -> requests.Response:
#     """
#     发送GET请求
#     :param url: 接口地址
#     :param params: 请求参数
#     :param headers: 请求头
#     :return: requests.Response对象
#     """
#     response = requests.get(url, params=params, headers=headers, timeout=10)
#     return response
#
#
# def api_test(start_mobile: int, count: int, delay: float):
#     """
#     主测试函数：循环发送请求，打印状态
#     :param start_mobile: 初始手机号
#     :param count: 请求次数
#     :param delay: 请求间隔（秒）
#     """
#     current_mobile = start_mobile
#     for i in range(1, count + 1):
#         params = build_params(current_mobile)
#         try:
#             response = send_request(BASE_URL, params, HEADERS)
#             print(f"请求次数: {i}")
#             print(f"手机号: {current_mobile}")
#             print(f"状态码: {response.status_code}")
#             try:
#                 # 尝试解析为JSON输出，如果失败则输出文本
#                 print(f"请求结果: {response.json()}")
#             except ValueError:
#                 print(f"请求结果: {response.text}")
#             print("-" * 50)
#         except requests.RequestException as e:
#             print(f"请求次数: {i} 出现异常: {e}")
#         current_mobile += 1  # 手机号自增
#         time.sleep(delay)  # 控制请求间隔
#
#
# # ==========================
# # 脚本入口
# # ==========================
# if __name__ == "__main__":
#     api_test(START_MOBILE, REQUEST_COUNT, DELAY_BETWEEN_REQUESTS)









# """
# 接口测试模块 - 用户搜索接口测试
# 功能：测试用户搜索接口，mobile参数自增，携带指定cookie
# 作者：测试团队
# 日期：2024
# """
#
# import requests
# import time
# from typing import Dict, Any, Optional
#
#
# # ==================== 配置区域 ====================
#
# # 接口基础地址
# BASE_URL = "https://crm.blzt888.com/crm_v2/system.user_search/index.html"
#
# # Cookie配置
# COOKIES = {
#     "jmftou": "003701fb978b67f42cf862a117d855dc"
# }
#
# # 固定请求参数
# FIXED_PARAMS = {
#     "spm": "m-204-254-411",
#     "app_userid": "",
#     "unionid": ""
# }
#
# # 测试配置
# TEST_CONFIG = {
#     "start_mobile": 13000000000,      # 起始手机号
#     "test_count": 10,                  # 测试次数
#     "request_interval": 1,            # 请求间隔(秒)
#     "timeout": 30                      # 请求超时时间(秒)
# }
#
#
# # ==================== 核心功能模块 ====================
#
# class UserSearchAPITester:
#     """
#     用户搜索接口测试类
#
#     该类封装了用户搜索接口的测试逻辑，包括：
#     - 参数构建
#     - 请求发送
#     - 响应验证
#     - 结果记录
#     """
#
#     def __init__(self, base_url: str, cookies: Dict[str, str], fixed_params: Dict[str, str]):
#         """
#         初始化测试器
#
#         Args:
#             base_url: 接口基础地址
#             cookies: Cookie字典
#             fixed_params: 固定请求参数字典
#         """
#         self.base_url = base_url
#         self.cookies = cookies
#         self.fixed_params = fixed_params
#         self.session = requests.Session()
#         self.test_results = []  # 存储测试结果
#
#     def build_request_params(self, mobile: int) -> Dict[str, Any]:
#         """
#         构建请求参数
#
#         Args:
#             mobile: 手机号码
#
#         Returns:
#             完整的请求参数字典
#         """
#         # 复制固定参数
#         params = self.fixed_params.copy()
#         # 添加动态参数
#         params["mobile"] = str(mobile)
#         return params
#
#     def send_request(self, params: Dict[str, Any], timeout: int = 30) -> Optional[requests.Response]:
#         """
#         发送HTTP请求
#
#         Args:
#             params: 请求参数字典
#             timeout: 超时时间(秒)
#
#         Returns:
#             Response对象，失败返回None
#         """
#         try:
#             # 发送GET请求
#             response = self.session.get(
#                 url=self.base_url,
#                 params=params,
#                 cookies=self.cookies,
#                 timeout=timeout,
#                 headers=self._get_headers()
#             )
#             return response
#
#         except requests.exceptions.Timeout:
#             print(f"❌ 请求超时: {self.base_url}")
#             return None
#         except requests.exceptions.ConnectionError:
#             print(f"❌ 连接错误: {self.base_url}")
#             return None
#         except requests.exceptions.RequestException as e:
#             print(f"❌ 请求异常: {str(e)}")
#             return None
#
#     def _get_headers(self) -> Dict[str, str]:
#         """
#         获取请求头
#
#         Returns:
#             请求头字典
#         """
#         return {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#             "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
#             "Accept-Encoding": "gzip, deflate, br",
#             "Connection": "keep-alive"
#         }
#
#     def validate_response(self, response: requests.Response) -> Dict[str, Any]:
#         """
#         验证响应结果
#
#         Args:
#             response: Response对象
#
#         Returns:
#             验证结果字典，包含状态、状态码、响应时间等信息
#         """
#         result = {
#             "status": "未知",
#             "status_code": response.status_code,
#             "response_time": response.elapsed.total_seconds(),
#             "content_length": len(response.content),
#             "content_type": response.headers.get('Content-Type', '未知'),
#             "url": response.url
#         }
#
#         # 根据状态码判断
#         if response.status_code == 200:
#             result["status"] = "成功 ✅"
#             # 尝试解析JSON响应（如果是JSON格式）
#             try:
#                 json_data = response.json()
#                 result["json_data"] = json_data
#                 result["is_json"] = True
#             except:
#                 result["is_json"] = False
#                 result["text_preview"] = response.text[:200] if response.text else ""
#         elif response.status_code == 404:
#             result["status"] = "资源不存在 ❌"
#         elif response.status_code == 500:
#             result["status"] = "服务器错误 ❌"
#         else:
#             result["status"] = f"异常状态 ⚠️"
#
#         return result
#
#     def print_result(self, mobile: int, result: Dict[str, Any]) -> None:
#         """
#         打印测试结果
#
#         Args:
#             mobile: 测试的手机号
#             result: 验证结果字典
#         """
#         print("\n" + "="*80)
#         print(f"📱 测试手机号: {mobile}")
#         print("-"*80)
#         print(f"状态: {result['status']}")
#         print(f"状态码: {result['status_code']}")
#         print(f"响应时间: {result['response_time']:.3f}秒")
#         print(f"内容长度: {result['content_length']} 字节")
#         print(f"内容类型: {result['content_type']}")
#         print(f"实际URL: {result['url']}")
#
#         # 如果是JSON响应，打印JSON数据
#         if result.get('is_json'):
#             print("\n📋 JSON响应数据:")
#             import json
#             print(json.dumps(result['json_data'], indent=2, ensure_ascii=False))
#         else:
#             # 打印文本预览
#             if result.get('text_preview'):
#                 print(f"\n📄 响应文本预览:\n{result['text_preview']}")
#
#         print("="*80)
#
#     def save_result(self, mobile: int, result: Dict[str, Any]) -> None:
#         """
#         保存测试结果到列表
#
#         Args:
#             mobile: 测试的手机号
#             result: 验证结果字典
#         """
#         self.test_results.append({
#             "mobile": mobile,
#             "result": result,
#             "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
#         })
#
#     def generate_summary(self) -> Dict[str, Any]:
#         """
#         生成测试摘要
#
#         Returns:
#             测试摘要字典
#         """
#         total = len(self.test_results)
#         success_count = sum(1 for item in self.test_results if item['result']['status_code'] == 200)
#         avg_response_time = sum(item['result']['response_time'] for item in self.test_results) / total if total > 0 else 0
#
#         summary = {
#             "总测试数": total,
#             "成功数": success_count,
#             "失败数": total - success_count,
#             "成功率": f"{(success_count/total*100):.2f}%" if total > 0 else "0%",
#             "平均响应时间": f"{avg_response_time:.3f}秒"
#         }
#
#         return summary
#
#
# # ==================== 执行函数模块 ====================
#
# def run_test():
#     """
#     执行接口测试主函数
#
#     该函数是整个测试流程的入口，负责：
#     1. 初始化测试器
#     2. 循环执行测试
#     3. 输出测试摘要
#     """
#     print("\n" + "🚀 "*20)
#     print(" " * 25 + "接口测试开始")
#     print("🚀 "*20 + "\n")
#
#     # 初始化测试器
#     tester = UserSearchAPITester(
#         base_url=BASE_URL,
#         cookies=COOKIES,
#         fixed_params=FIXED_PARAMS
#     )
#
#     # 获取配置
#     start_mobile = TEST_CONFIG["start_mobile"]
#     test_count = TEST_CONFIG["test_count"]
#     interval = TEST_CONFIG["request_interval"]
#     timeout = TEST_CONFIG["timeout"]
#
#     print(f"📊 测试配置:")
#     print(f"  - 起始手机号: {start_mobile}")
#     print(f"  - 测试次数: {test_count}")
#     print(f"  - 请求间隔: {interval}秒")
#     print(f"  - 超时时间: {timeout}秒")
#     print(f"  - 接口地址: {BASE_URL}")
#     print(f"  - Cookie: {COOKIES}")
#     print("\n" + "="*80)
#
#     # 循环执行测试
#     for i in range(test_count):
#         current_mobile = start_mobile + i
#
#         print(f"\n⏳ 正在测试第 {i+1}/{test_count} 次...")
#
#         # 构建参数
#         params = tester.build_request_params(current_mobile)
#
#         # 发送请求
#         response = tester.send_request(params, timeout)
#
#         if response:
#             # 验证响应
#             result = tester.validate_response(response)
#
#             # 打印结果
#             tester.print_result(current_mobile, result)
#
#             # 保存结果
#             tester.save_result(current_mobile, result)
#         else:
#             print(f"❌ 请求失败，跳过手机号 {current_mobile}")
#
#         # 延时（避免请求过快）
#         if i < test_count - 1:  # 最后一次不需要延时
#             time.sleep(interval)
#
#     # 生成测试摘要
#     print("\n\n" + "📊 "*20)
#     print(" " * 25 + "测试摘要")
#     print("📊 "*20 + "\n")
#
#     summary = tester.generate_summary()
#     for key, value in summary.items():
#         print(f"  {key}: {value}")
#
#     print("\n" + "="*80)
#     print("✅ 测试完成！")
#     print("="*80 + "\n")
#
#     return tester.test_results
#
#
# def save_results_to_file(results: list, filename: str = "test_results.json"):
#     """
#     将测试结果保存到JSON文件
#
#     Args:
#         results: 测试结果列表
#         filename: 输出文件名
#     """
#     import json
#     import os
#
#     try:
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(results, f, indent=2, ensure_ascii=False)
#         print(f"✅ 测试结果已保存到: {os.path.abspath(filename)}")
#     except Exception as e:
#         print(f"❌ 保存文件失败: {str(e)}")
#
#
# # ==================== 主程序入口 ====================
#
# if __name__ == "__main__":
#     """
#     主程序入口
#
#     执行流程：
#     1. 运行测试
#     2. 保存结果到文件
#     """
#     print("\n" + "="*80)
#     print(" " * 25 + "用户搜索接口测试程序")
#     print(" " * 25 + "User Search API Tester")
#     print("="*80 + "\n")
#
#     # 执行测试
#     test_results = run_test()
#
#     # 保存结果到文件
#     save_results_to_file(test_results, "user_search_test_results.json")
#
#     print("\n🎉 所有测试已完成！\n")
