#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, jsonify
import requests
import csv
import os
from functools import wraps
import logging
import json
from datetime import datetime, timedelta
import jwt
import base64
import urllib3
import configparser
import time
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# 忽略HTTPS警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置文件读取
config = configparser.ConfigParser()
config.read('config.ini')

# API配置
url_get_chat_log = config.get('API', 'url_get_chat_log')
url_get_order_list = config.get('API', 'url_get_order_list')
url_submit = config.get('API', 'url_submit')
url_crm = config.get('API', 'url_crm')
appsecret = config.get('API', 'appsecret')
agent = config.get('API', 'agent')
appid = config.get('API', 'appid')
aes_DEFAULT_KEY = config.get('API', 'aes_DEFAULT_KEY')

# 密钥路径配置
public_key_path = config.get('Keys', 'public_key_path')
private_key_path = config.get('Keys', 'private_key_path')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('log/wai.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 全局配置
API_KEY = "yashang_api_key_test_lkd"
BASE_DIR = "messages"
SECRET_KEY = 'yashang_jwt_key_test_lkd'

os.makedirs(BASE_DIR, exist_ok=True)

# ============================== 加解密及上传函数集成 ==============================

def rsa_encrypt(data, public_key_path):
    with open(public_key_path, 'r') as f:
        key = RSA.import_key(f.read())
    cipher = Cipher_pkcs1_v1_5.new(key)
    default_length = 245
    data_bytes = data.encode('utf-8')
    encrypted = b''.join([cipher.encrypt(data_bytes[i:i+default_length]) for i in range(0, len(data_bytes), default_length)])
    return base64.b64encode(encrypted).decode('utf-8')

def aes_decrypt(data, key):
    cipher = AES.new(key.ljust(32, '\0').encode('utf-8'), AES.MODE_ECB)
    decrypted = cipher.decrypt(base64.b64decode(data))
    try:
        return decrypted.decode('utf-8').strip()
    except Exception:
        return decrypted.strip()

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

def upload_to_crm(data, public_key_path, private_key_path, url_crm, appsecret, agent, appid):
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

# ============================== 业务辅助函数 ==============================

def save_message_to_csv(message):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(BASE_DIR, f"messages_{current_date}.csv")
    file_exists = os.path.isfile(filename)

    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['conversation_id', 'user_id', 'costumer_id', 'order_id', 'msg_id', 'table_name',
                                 'external_userid', 'userid', 'content', 'event', 'event_score', 'event_level',
                                 'reason', 'indexs', 'eventType'])

            data = message.get('data', {})
            conversation_id = data.get('conversation_id')
            user_id = data.get('user_id', '')
            costumer_id = data.get('costumer_id', '')
            order_id = data.get('order_id', '')
            msgs = data.get('msgs', [])

            for msg in msgs:
                msg_id = msg.get('msg_id', '')
                table_name = msg.get('table_name', '')
                external_userid = msg.get('external_userid', '')
                userid = msg.get('userid', '')
                content = msg.get('content', '')
                events = msg.get('events', [])
                for event in events:
                    row = [
                        conversation_id, user_id, costumer_id, order_id, msg_id, table_name,
                        external_userid, userid, content, event.get('event', ''),
                        event.get('event_score', ''), event.get('event_level', ''),
                        event.get('reason', ''), ','.join(map(str, event.get('indexs', []))),
                        event.get('eventType', '')
                    ]
                    writer.writerow(row)
        return f"消息已成功保存到 {filename}"
    except Exception as e:
        logger.error(f"保存消息到CSV文件时发生错误: {e}")
        return f"保存消息失败: {e}"

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get("X-API-KEY")
        if provided_key != API_KEY:
            logger.warning(f"无效的 API 密钥: {provided_key}")
            return jsonify({"error": "无效的 API 密钥", "status": "failed"}), 401
        return view_function(*args, **kwargs)
    return decorated_function

def restrict_ip(view_function):
    ALLOWED_IPS = ['112.64.108.74', '39.108.67.223', '47.96.43.100', '115.29.240.205']
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            logger.warning(f"拒绝来自 {client_ip} 的请求")
            return jsonify({"error": "IP 地址未授权", "status": "failed"}), 403
        return view_function(*args, **kwargs)
    return decorated_function

def token_required(view_function):
    @wraps(view_function)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and len(auth_header.split()) == 2:
            token = auth_header.split()[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['sub']
        except Exception as e:
            logger.error(f"Token 解码错误: {e}")
            return jsonify({'message': 'Token is invalid!'}), 403
        return view_function(current_user, *args, **kwargs)
    return decorated

# ============================== 路由 ==============================

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        logger.info(f"登录数据：{data}")
        if not data or 'username' not in data or 'password' not in data:
            logger.error("登录请求缺少必要的用户名或密码字段")
            return jsonify({"error": "Invalid credentials", "status": "failed"}), 400
        username = data['username']
        password = data['password']
        if username == "yashang_test_user" and password == "yashang_test_password":
            token = jwt.encode({
                'sub': username,
                'exp': datetime.utcnow() + timedelta(minutes=30)
            }, SECRET_KEY, algorithm="HS256")
            logger.info(f"成功生成JWT令牌给用户: {username} token: {token}")
            return jsonify({'token': token}), 200
        logger.warning(f"无效的登录凭据对于用户: {username}")
        return jsonify({"error": "Invalid credentials", "status": "failed"}), 401
    except Exception as e:
        logger.error(f"处理登录请求时发生错误: {e}")
        return jsonify({"error": "Internal Server Error", "status": "failed"}), 500

@app.route('/receive-message', methods=['POST'])
@require_api_key
@restrict_ip
@token_required
def receive_message(current_user):
    try:
        raw_data = request.get_data(as_text=True)
        if not raw_data:
            logger.error("未接收到任何数据")
            return jsonify({"error": "未接收到任何数据", "status": "failed"}), 400

        json_obj = None
        is_encrypted = False
        try:
            json_obj = json.loads(raw_data)
            base64.b64decode(json_obj['data'], validate=True)
            is_encrypted = True
        except (base64.binascii.Error, ValueError, KeyError, json.JSONDecodeError):
            is_encrypted = False

        if is_encrypted:
            decrypted_data = aes_de(json_obj['data'], aes_DEFAULT_KEY)
            logger.info(f"解密AI返回数据：{decrypted_data}")
            if not decrypted_data:
                logger.error("解密失败或解密结果为空")
                return jsonify({"error": "解密失败", "status": "failed"}), 400
            data = decrypted_data
        else:
            data = raw_data

        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"数据无法解析为 JSON: {e}")
            return jsonify({"error": "数据格式无效", "status": "failed"}), 400

        if not isinstance(parsed_data, dict) or 'data' not in parsed_data or 'msgs' not in parsed_data['data']:
            logger.error("无效的消息格式: 数据必须包含 'data' 和 'msgs' 字段")
            return jsonify({"error": "无效的消息格式", "status": "failed"}), 400

        conversation_id = parsed_data.get('data', {}).get('conversation_id')
        msgs = parsed_data['data'].get('msgs', [])

        if not conversation_id:
            logger.warning("conversation_id 为空或不存在，跳过该条数据的处理")
            return jsonify({"message": "conversation_id 为空或不存在，跳过该条数据", "status": "skipped"}), 200

        if not msgs:
            parsed_data['data']['msgs'] = ['AI审查未发现问题']
            parsed_data['data']['is_msgs'] = 1
            logger.info("AI审查未发现问题，跳过保存CSV文件的步骤")
        else:
            parsed_data['data']['is_msgs'] = 0
            result = save_message_to_csv(parsed_data)
            logger.info(f"消息已成功保存到本地CSV文件: {result}")

        # 上传至CRM
        res_upload = upload_to_crm(parsed_data, public_key_path, private_key_path, url_crm, appsecret, agent, appid)
        try:
            res_data = json.loads(res_upload)
            if res_data.get('msg') == 'success':
                logger.info(f"AI返回结果成功上传至CRM系统。返回数据: {res_data}")
            else:
                error_msg = res_data.get('msg', '未知错误')
                logger.error(f"上传至CRM系统失败。错误信息: {error_msg}, 返回数据: {res_data}")
        except Exception:
            logger.error(f"无法解析 upload_to_crm 的返回值为JSON。原始返回值: {res_upload}")

        return jsonify({"message": "消息处理完成", "status": "success"}), 200

    except requests.exceptions.RequestException as req_err:
        logger.error(f"请求CRM系统时发生网络错误: {req_err}")
        return jsonify({"error": f"请求CRM系统失败: {str(req_err)}", "status": "failed"}), 500
    except Exception as e:
        logger.error(f"处理消息时发生未知错误: {e}")
        return jsonify({"error": str(e), "status": "failed"}), 500

if __name__ == '__main__':
    logger.info("Flask 应用已启动")
    app.run(host='0.0.0.0', port=4000, debug=False, ssl_context='adhoc')