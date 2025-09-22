#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pika
import time
import json
import hashlib
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import urllib3
import configparser
from datetime import datetime
import logging
import re

# ========== 全局配置 ==========
BASE_PATH = r'C:\Users\Administrator\Desktop\services\HighRiskCustomers'
os.makedirs(BASE_PATH, exist_ok=True)
sys.path.append(BASE_PATH)
LOG_FILE = os.path.join(BASE_PATH, 'log/log.log')
CONFIG_FILE = os.path.join(BASE_PATH, 'config.ini')

# ========== 日志设置 ==========
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# ========== 配置读取 ==========
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
required_api_keys = ['url_submit_alert', 'url_es', 'appsecret', 'agent', 'appid', 'aes_DEFAULT_KEY']
missing_api_keys = [key for key in required_api_keys if not config.has_option('API', key)]
if missing_api_keys:
    logger.error(f"缺少以下配置项: {', '.join(missing_api_keys)}")
    sys.exit(1)
appsecret = config.get('API', 'appsecret')
agent = config.get('API', 'agent')
appid = config.get('API', 'appid')
aes_DEFAULT_KEY = config.get('API', 'aes_DEFAULT_KEY')
url_es = config.get('API', 'url_es')
url_crm_alert = config.get('API', 'url_crm_alert')
url_submit_alert = config.get('API', 'url_submit_alert')
public_key_path = config.get('Keys', 'public_key_path')
private_key_path = config.get('Keys', 'private_key_path')
for path in [public_key_path, private_key_path]:
    if not os.path.exists(path):
        logger.error(f"密钥文件未找到: {path}")
        sys.exit(1)

# ========== RabbitMQ 配置 ==========
rabbitmq_config = {
    'host': '120.27.153.144',
    'port': 5672,
    'user': 'bladmin',
    'pass': 'Bl@RabBmq957FoR@P157',
    'exchange': 'ai_customer_alert',
    'queue_name': 'ai_customer_alert_queue',
    'routing_key': 'public'
}

# ========== 自定义字段映射 ==========
custom_map = {
    'msgId': 'msgid',
    'highRiskRecordId': 'work_wechat_high_risk_customers_id',
    'keywordLogId': 'work_wechat_keyword_log_id',
    'tableName': 'table_name',
    'appId': 'appid',
    'isAlert': 'is_alert',
    'riskLevel': 'risk_level',
    'riskEvents': 'events'
}

# ========== 工具函数 ==========
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def rsa_encrypt(data, public_key_path):
    with open(public_key_path, 'r') as f:
        key = RSA.import_key(f.read())
    cipher = Cipher_pkcs1_v1_5.new(key)
    default_length = 245
    data_bytes = data.encode('utf-8')
    encrypted = b''.join([cipher.encrypt(data_bytes[i:i+default_length]) for i in range(0, len(data_bytes), default_length)])
    return base64.b64encode(encrypted).decode('utf-8')

def aes_decrypt(data, key):
    cipher = AES.new(key.ljust(32, '\0').encode(), AES.MODE_ECB)
    decrypted = cipher.decrypt(base64.b64decode(data)).strip().decode()
    return decrypted

def aes_en(plain_text: str, key: str) -> str:
    try:
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    except Exception as e:
        logger.error(f"加密失败: {e}")
        return None

def aes_de(encrypted_text: str, key: str) -> str:
    try:
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"解密失败: {e}")
        return None

def validate_and_parse_json(decrypted_result):
    try:
        return [json.loads(decrypted_result)]
    except json.JSONDecodeError as e:
        if "Extra data" in str(e):
            pos = e.pos
            valid_json, extra_data = decrypted_result[:pos], decrypted_result[pos:]
            results = [json.loads(valid_json)]
            extra_data = extra_data.lstrip(', ')
            if extra_data:
                results.extend(validate_and_parse_json(extra_data))
            return results
        else:
            return []

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def convert_dict_keys(data, custom_map):
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_key = custom_map.get(key, to_snake_case(key))
            new_dict[new_key] = convert_dict_keys(value, custom_map)
        return new_dict
    elif isinstance(data, list):
        return [convert_dict_keys(item, custom_map) for item in data]
    else:
        return data

def upload_to_crm(data, public_key_path, private_key_path, url_crm, appsecret, agent, appid):
    msgs_str = json.dumps(data['data']['msgs'], ensure_ascii=False)
    data['data']['msgs'] = msgs_str
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

def fetch_and_decrypt_alert_chat(data, public_key_path, private_key_path, url_es, appsecret, agent, appid):
    timestamp = str(int(time.time()))
    nonce = hashlib.md5(str(time.time()).encode()).hexdigest()[4:16]
    request_data = {
        "appid": data.get("appid"),
        "msgid": data.get("msgid"),
        "content": data.get("content"),
        "roomid": data.get("roomid"),
        "is_roomid": data.get("is_roomid"),
        "is_saleman": data.get("is_saleman"),
        "msgtime": data.get("msgtime"),
        "msgtype": data.get("msgtype"),
        "table_name": data.get("table_name"),
        "work_wechat_high_risk_customers_id": data.get("work_wechat_high_risk_customers_id"),
        "work_wechat_keyword_log_id": data.get("work_wechat_keyword_log_id"),
        "tolist": data.get("tolist"),
        "from": data.get("from")
    }
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted(request_data.items()) if v is not None]) + f"&appsecret={appsecret}"
    sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
    headers = {
        'Agent': agent,
        'Content-Type': 'application/json;charset=utf-8',
        'Appid': appid,
        'Timestamp': timestamp,
        'Nonce': nonce,
        'Sign': sign
    }
    encrypted_data = rsa_encrypt(json.dumps(request_data), public_key_path)
    response = requests.post(url_es, headers=headers, data=encrypted_data, verify=False)
    try:
        result = response.json()
    except json.JSONDecodeError:
        return f"响应解析失败：{response.text}"
    if result.get('code') == 200:
        try:
            with open(private_key_path, 'r') as f:
                key = RSA.importKey(f.read())
                cipher = Cipher_pkcs1_v1_5.new(key)
                encrypt_key = result['data']['encryptKey']
                aes_key = cipher.decrypt(base64.b64decode(encrypt_key), None).decode()
            encrypt_data = result['data']['encryptData']
            decrypted_result = aes_decrypt(encrypt_data, aes_key)
            final_result = json.loads(decrypted_result[decrypted_result.find('{'):decrypted_result.rfind('}')+1])
            return final_result
        except Exception as decrypt_error:
            return f"解密失败: {decrypt_error}"
    else:
        error_msg = result.get('msg', '未知错误')
        return error_msg

def serialize_data(data):
    try:
        return json.dumps(data)
    except Exception as e:
        logger.error(f"JSON 序列化失败: {e}")
        return None

def encrypt_data(plain_text, key):
    encrypted = aes_en(plain_text, key)
    if not encrypted:
        logger.error("AES 加密返回空值")
        return None
    return encrypted

def send_to_ai_api(url, headers, encrypted_data):
    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps({"data": encrypted_data}),
            timeout=(5, 30),
            verify=False
        )
        response.raise_for_status()
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        raise

# ========== 回调函数 ==========
def callback(ch, method, properties, body):
    try:
        message_str = body.decode('utf-8')
        message_dict = json.loads(message_str)
        logger.info(f"收到消息: {message_dict.get('content', '')}")

        time.sleep(1)

        # 获取并解密 ES 数据
        result = fetch_and_decrypt_alert_chat(message_dict, public_key_path, private_key_path, url_es, appsecret, agent, appid)
        if not result:
            logger.warning("获取或解密数据为空，跳过处理")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # 序列化
        plain_text = serialize_data(result)
        if not plain_text:
            return

        # 加密
        encrypted_data = encrypt_data(plain_text, aes_DEFAULT_KEY)
        if not encrypted_data:
            return

        # 调用 AI 接口
        try:
            final_result = send_to_ai_api(url_submit_alert, {
                'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
                'Content-Type': 'application/json'
            }, encrypted_data)
        except Exception as e:
            logger.error(f"请求出错: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        logger.info(f"AI返回数据: {final_result}")

        # 解密 AI 返回结果
        if isinstance(final_result, dict) and 'data' in final_result:
            decrypted_data = aes_de(final_result['data'], aes_DEFAULT_KEY)
        else:
            logger.error("AI 接口返回格式错误，缺少 'data' 字段")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        parsed_data = json.loads(decrypted_data)
        final_result['data'] = parsed_data

        logger.info(f"准备上传到 CRM 的数据: {final_result}")

        # 调用 CRM 接口
        try:
            r = upload_to_crm(final_result, public_key_path, private_key_path, url_crm_alert, appsecret, agent, appid)
            try:
                r_json = json.loads(r) if isinstance(r, str) else r
            except json.JSONDecodeError:
                r_json = None
            if isinstance(r_json, dict) and r_json.get("errcode") == 0:
                logger.info("成功上传CRM系统")
            else:
                logger.warning(f"上传 CRM 失败，返回内容: {r}")
        except Exception as e:
            logger.error(f"调用 upload_to_crm 失败: {e}", exc_info=True)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"处理消息失败: {e}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# ========== 主程序入口 ==========
def start_consumer():
    while True:
        try:
            credentials = pika.PlainCredentials(rabbitmq_config['user'], rabbitmq_config['pass'])
            parameters = pika.ConnectionParameters(
                host=rabbitmq_config['host'],
                port=rabbitmq_config['port'],
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=rabbitmq_config['queue_name'], durable=True)
            channel.queue_bind(
                exchange=rabbitmq_config['exchange'],
                queue=rabbitmq_config['queue_name'],
                routing_key=rabbitmq_config['routing_key']
            )
            logger.info(f"已绑定交换机 '{rabbitmq_config['exchange']}' 和 routing key '{rabbitmq_config['routing_key']}'")
            logger.info('等待接收消息...')
            channel.basic_consume(
                queue=rabbitmq_config['queue_name'],
                on_message_callback=callback,
                auto_ack=False
            )
            logger.info('开始监听队列，将持续消费消息...')
            channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            logger.warning("RabbitMQ 连接被服务器关闭，将在5秒后重连...")
            time.sleep(5)
        except pika.exceptions.AMQPConnectionError:
            logger.error("与 RabbitMQ 的连接中断，尝试重新连接...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"发生未知错误: {e}", exc_info=True)
            time.sleep(5)

if __name__ == '__main__':
    try:
        start_consumer()
    except KeyboardInterrupt:
        logger.info("用户中断消费者")
    except Exception as e:
        logger.error(f"消费者异常退出: {e}", exc_info=True)