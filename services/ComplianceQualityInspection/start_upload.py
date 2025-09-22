#!/usr/bin/env python
# coding: utf-8

import sys
import os
import json
import logging
import configparser
import hashlib
from datetime import datetime, timedelta
from time import sleep
import requests
import urllib3
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# 1. 路径与全局配置
BASE_PATH = os.getenv('SERVICE_BASE_PATH', r'C:\Users\Administrator\Desktop\services\ComplianceQualityInspection')
CONFIG_FILE = os.path.join(BASE_PATH, 'config.ini')
LOG_FILE = os.path.join(BASE_PATH, 'log/upload.log')
PUBLIC_KEY_FILENAME = 'public_key.pem'
PRIVATE_KEY_FILENAME = 'private_key.pem'
public_key_path = os.path.join(BASE_PATH, PUBLIC_KEY_FILENAME)
private_key_path = os.path.join(BASE_PATH, PRIVATE_KEY_FILENAME)

# 2. 日志配置
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 3. 忽略https警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 4. 所有自定义函数整合如下
def rsa_encrypt(data, public_key_path):
    """RSA加密数据（长数据分段）"""
    with open(public_key_path, 'r') as f:
        key = RSA.import_key(f.read())
    cipher = Cipher_pkcs1_v1_5.new(key)
    default_length = 245
    data_bytes = data.encode('utf-8')
    encrypted = b''.join([cipher.encrypt(data_bytes[i:i+default_length]) for i in range(0, len(data_bytes), default_length)])
    return base64.b64encode(encrypted).decode('utf-8')


def aes_decrypt(data, key):
    """AES解密（ECB模式，无IV）"""
    cipher = AES.new(key.ljust(32, '\0').encode('utf-8'), AES.MODE_ECB)
    decrypted = cipher.decrypt(base64.b64decode(data))
    try:
        return decrypted.decode('utf-8').strip()
    except Exception:
        return decrypted.strip()


def validate_and_parse_json(decrypted_result):
    """递归解析可能有'Extra data'异常的JSON串，返回完整对象列表"""
    try:
        return [json.loads(decrypted_result)]
    except json.JSONDecodeError as e:
        if "Extra data" in str(e):
            pos = e.pos
            valid_json, extra_data = decrypted_result[:pos], decrypted_result[pos:]
            result = [json.loads(valid_json)]
            extra_data = extra_data.lstrip(', ')
            if extra_data:
                result.extend(validate_and_parse_json(extra_data))
            return result
        return []


def generate_conversation_id(a_id, b_id):
    """对两个ID排序后MD5生成conversation_id"""
    sorted_ids = sorted([a_id, b_id])
    combined = f"{sorted_ids[0]}|{sorted_ids[1]}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()


def replace_with_conversation_id(data):
    """把user_id和costumer_id转为conversation_id，并置于首位"""
    for item in data:
        user_id = item.get('user_id')
        costumer_id = item.get('costumer_id')
        if user_id and costumer_id:
            conv_id = generate_conversation_id(user_id, costumer_id)
            new_item = {'conversation_id': conv_id}
            new_item.update(item)
            item.clear()
            item.update(new_item)
    return data


def fetch_and_decrypt_chat_log(order_id, public_key_path, private_key_path, url, appsecret, agent, appid):
    """获取并解密订单聊天记录"""
    timestamp = str(int(time.time()))
    nonce = hashlib.md5(str(time.time()).encode()).hexdigest()[4:16]
    data = {'order_id': order_id}
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted(data.items())]) + f"&appsecret={appsecret}"
    sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
    headers = {
        'Agent': agent,
        'Content-Type': 'application/json;charset=utf-8',
        'Appid': appid,
        'Timestamp': timestamp,
        'Nonce': nonce,
        'Sign': sign
    }
    encrypted_data = rsa_encrypt(json.dumps(data), public_key_path)
    response = requests.post(url, headers=headers, data=encrypted_data, verify=False)
    result = response.json()
    if result.get('errcode') == 0:
        with open(private_key_path, 'r') as f:
            key = RSA.import_key(f.read())
        cipher = Cipher_pkcs1_v1_5.new(key)
        aes_key = cipher.decrypt(base64.b64decode(result['data']['encryptKey']), None).decode('utf-8')
        decrypted_result = aes_decrypt(result['data']['encryptData'], aes_key)
        return decrypted_result
    return result.get('msg', 'Unknown error')


def fetch_and_decrypt_order_list(start_time_string, end_time_string, order_range, public_key_path, private_key_path, url, appsecret, agent, appid):
    """获取并解密订单号列表"""
    timestamp = str(int(time.time()))
    nonce = hashlib.md5(str(time.time()).encode()).hexdigest()[4:16]
    start_dt = datetime.strptime(start_time_string, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end_time_string, "%Y-%m-%d %H:%M:%S")
    data = {
        'start': str(int(start_dt.timestamp())),
        'end': str(int(end_dt.timestamp())),
        'range': order_range
    }
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted(data.items())]) + f"&appsecret={appsecret}"
    sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
    headers = {
        'Agent': agent,
        'Content-Type': 'application/json;charset=utf-8',
        'Appid': appid,
        'Timestamp': timestamp,
        'Nonce': nonce,
        'Sign': sign
    }
    encrypted_data = rsa_encrypt(json.dumps(data), public_key_path)
    response = requests.post(url, headers=headers, data=encrypted_data, verify=False)
    result = response.json()
    if result.get('errcode') == 0:
        data_block = None
        if not result.get('data'):
            return []
        if isinstance(result['data'], list) and result['data']:
            data_block = result['data'][0]
        elif isinstance(result['data'], dict):
            data_block = result['data']
        else:
            return []
        with open(private_key_path, 'r') as f:
            key = RSA.import_key(f.read())
        cipher = Cipher_pkcs1_v1_5.new(key)
        aes_key = cipher.decrypt(base64.b64decode(data_block['encryptKey']), None).decode('utf-8')
        decrypted_result = aes_decrypt(data_block['encryptData'], aes_key)
        order_number_list = validate_and_parse_json(decrypted_result)[0]
        return order_number_list
    return []


def upload_to_crm(data, public_key_path, private_key_path, url_crm, appsecret, agent, appid):
    """上传AI审查结果到CRM"""
    data['data']['msgs'] = json.dumps(data['data']['msgs'], ensure_ascii=False)
    data_test = data['data']
    timestamp = str(int(time.time()))
    nonce = hashlib.md5(str(time.time()).encode()).hexdigest()[4:16]
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted(data_test.items())]) + f"&appsecret={appsecret}"
    sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
    headers = {
        'Agent': agent,
        'Content-Type': 'application/json;charset=utf-8',
        'Appid': appid,
        'Timestamp': timestamp,
        'Nonce': nonce,
        'Sign': sign
    }
    encrypted_data = rsa_encrypt(json.dumps(data_test), public_key_path)
    response = requests.post(url_crm, headers=headers, data=encrypted_data, verify=False)
    return response.text


def aes_en(plain_text: str, key: str) -> str:
    """AES加密（ECB模式，无IV）"""
    try:
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    except Exception as e:
        print(f"加密失败: {e}")
        return None


def aes_de(encrypted_text: str, key: str) -> str:
    """AES解密（ECB模式，无IV）"""
    try:
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"解密失败: {e}")
        return None

# 5. 配置读取与校验
def load_and_validate_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    required_api_keys = [
        'url_get_chat_log', 'url_get_order_list', 'url_submit_formal',
        'appsecret', 'agent', 'appid', 'preprocess', 'aes_DEFAULT_KEY'
    ]
    required_key_paths = ['public_key_path', 'private_key_path']
    missing_api_keys = [k for k in required_api_keys if not config.has_option('API', k)]
    missing_key_paths = [k for k in required_key_paths if not config.has_option('Keys', k)]
    if missing_api_keys or missing_key_paths:
        msg = ""
        if missing_api_keys:
            msg += f"API 配置缺少参数: {', '.join(missing_api_keys)}\n"
        if missing_key_paths:
            msg += f"密钥路径配置缺少参数: {', '.join(missing_key_paths)}"
        logging.error(msg.strip())
        sys.exit(1)
    return config

def check_key_files():
    if not os.path.exists(public_key_path):
        logging.error(f"公钥文件未找到: {public_key_path}")
        sys.exit(1)
    if not os.path.exists(private_key_path):
        logging.error(f"私钥文件未找到: {private_key_path}")
        sys.exit(1)

# 6. 日志统计工具
def log_stats(stats, prefix=""):
    logging.info(f"{prefix}订单总数: {stats['total']}")
    logging.info(f"{prefix}成功: {stats['success']}，失败: {stats['failed']}，跳过: {stats['skipped']}")

# 7. 主流程
def main():
    config = load_and_validate_config()
    check_key_files()

    url_get_chat_log = config.get('API', 'url_get_chat_log')
    url_get_order_list = config.get('API', 'url_get_order_list')
    url_submit = config.get('API', 'url_submit_formal')
    appsecret = config.get('API', 'appsecret')
    agent = config.get('API', 'agent')
    appid = config.get('API', 'appid')
    preprocess = int(config.get('API', 'preprocess'))
    aes_DEFAULT_KEY = config.get('API', 'aes_DEFAULT_KEY')
    access_token = config.get('API', 'access_token', fallback='YOUR_ACCESS_TOKEN')

    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    start_time_string = one_hour_ago.strftime("%Y-%m-%d %H:%M:%S")
    end_time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    stats = {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}
    task_start_time = datetime.now()
    logging.info("任务开始时间: %s", task_start_time.strftime('%Y-%m-%d %H:%M:%S'))

    try:
        order_ids = fetch_and_decrypt_order_list(
            start_time_string, end_time_string, 'all',
            public_key_path, private_key_path,
            url_get_order_list, appsecret, agent, appid
        )
    except Exception as e:
        logging.error(f"获取订单列表失败: {str(e)}")
        sys.exit(1)

    if not order_ids:
        logging.warning("未获取到订单数据，任务提前结束")
        log_stats(stats, "任务结束")
        return

    stats['total'] = len(order_ids)
    log_stats(stats, prefix="任务获取订单")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    for order_id in map(str, order_ids):
        logging.info(f"正在质检订单：{order_id}")
        sleep(0.2)
        try:
            decrypted = fetch_and_decrypt_chat_log(
                order_id, public_key_path, private_key_path,
                url_get_chat_log, appsecret, agent, appid
            )
            json_content = replace_with_conversation_id(validate_and_parse_json(decrypted))
            if not json_content or not isinstance(json_content[0], dict):
                logging.error(f"订单 {order_id} 的 JSON 数据格式不正确或为空，跳过")
                stats['skipped'] += 1
                continue

            json_content[0]['preprocess'] = preprocess
            plain_text = json.dumps(json_content[0], ensure_ascii=False)
            encrypted_data = aes_en(plain_text, aes_DEFAULT_KEY)
            if not encrypted_data:
                logging.error(f"订单 {order_id} AES加密失败，跳过")
                stats['skipped'] += 1
                continue

            payload = json.dumps({"data": encrypted_data})
            try:
                response = requests.post(url_submit, headers=headers, data=payload, timeout=30)
            except Exception as ex:
                logging.error(f"订单 {order_id} 请求上传异常: {ex}")
                stats['failed'] += 1
                continue

            if response.status_code == 200:
                logging.info(f"质检订单号：{order_id} 上传成功")
                stats['success'] += 1
            else:
                stats['failed'] += 1
                logging.error(f"订单 {order_id} 上传失败，状态码: {response.status_code}, 响应内容: {response.text[:500]}")

        except json.JSONDecodeError as jde:
            stats['failed'] += 1
            logging.error(f"订单 {order_id} JSON解析错误: {jde}")
        except Exception as e:
            stats['failed'] += 1
            logging.error(f"订单 {order_id} 处理失败: {e}")

    task_end_time = datetime.now()
    logging.info("任务结束时间: %s", task_end_time.strftime('%Y-%m-%d %H:%M:%S'))
    logging.info(f"任务总运行时间: {task_end_time - task_start_time}")
    log_stats(stats, "任务最终")

if __name__ == "__main__":
    main()