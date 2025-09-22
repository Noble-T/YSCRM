# -*- coding: utf-8 -*-
# 单文件版：Web批量上传前端+服务端及所有加解密、接口和上传逻辑
from flask import Flask, request, render_template_string, jsonify
import sys
import os
import threading
import time
import json
import hashlib
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from datetime import datetime
import urllib3
import configparser
import logging

# ====================== 配置部分 ======================
BASE_PATH = r'C:\Users\Administrator\Desktop\services\ComplianceQualityInspection'
sys.path.append(BASE_PATH)

LOG_FILE = os.path.join(BASE_PATH, 'log/nei.log')
CONFIG_FILE = os.path.join(BASE_PATH, 'config.ini')
PUBLIC_KEY_FILENAME = 'public_key.pem'
PRIVATE_KEY_FILENAME = 'private_key.pem'
public_key_path = os.path.join(BASE_PATH, PUBLIC_KEY_FILENAME)
private_key_path = os.path.join(BASE_PATH, PRIVATE_KEY_FILENAME)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 配置读取和校验
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
required_api_keys = [
    'url_get_chat_log', 'url_get_order_list', 'url_submit_encrypted',
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
# API配置
url_get_chat_log = config.get('API', 'url_get_chat_log')
url_get_order_list = config.get('API', 'url_get_order_list')
url_submit = config.get('API', 'url_submit_encrypted')
appsecret = config.get('API', 'appsecret')
agent = config.get('API', 'agent')
appid = config.get('API', 'appid')
preprocess = int(config.get('API', 'preprocess'))
aes_DEFAULT_KEY = config.get('API', 'aes_DEFAULT_KEY')
# 检查密钥文件
if not os.path.exists(public_key_path):
    logging.error(f"公钥文件未找到: {public_key_path}")
    sys.exit(1)
if not os.path.exists(private_key_path):
    logging.error(f"私钥文件未找到: {private_key_path}")
    sys.exit(1)

# ====================== 加解密及业务函数 ======================
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

def validate_and_parse_json(decrypted_result):
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
    sorted_ids = sorted([a_id, b_id])
    combined = f"{sorted_ids[0]}|{sorted_ids[1]}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def replace_with_conversation_id(data):
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

def aes_en(plain_text: str, key: str) -> str:
    try:
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    except Exception as e:
        print(f"加密失败: {e}")
        return None

def aes_de(encrypted_text: str, key: str) -> str:
    try:
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"解密失败: {e}")
        return None

def upload_multiple_orders(order_ids, progress_callback=None):
    success_orders = []
    failed_orders = []
    total_orders = len(order_ids)
    for index, order_id in enumerate(order_ids):
        time.sleep(0.2)
        try:
            decrypted_result = fetch_and_decrypt_chat_log(
                order_id, public_key_path, private_key_path,
                url_get_chat_log, appsecret, agent, appid
            )
            try:
                json_content = replace_with_conversation_id(validate_and_parse_json(decrypted_result))
                if json_content != []:
                    if isinstance(json_content[0], dict):
                        json_content[0]['preprocess'] = preprocess
                    else:
                        logging.error(f"订单 {order_id} 的 JSON 数据格式不正确，无法设置 preprocess 参数")
                        failed_orders.append(order_id)
                        continue

                    plain_text = json.dumps(json_content[0], ensure_ascii=False)
                    encrypted_data = aes_en(plain_text, aes_DEFAULT_KEY)
                    if not encrypted_data:
                        logging.error(f"订单 {order_id} 数据加密失败，跳过处理")
                        failed_orders.append(order_id)
                        continue

                    headers = {
                        'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
                        'Content-Type': 'application/json'
                    }
                    response = requests.post(url_submit, headers=headers, data=json.dumps({"data": encrypted_data}), timeout=30)
                    if response.status_code == 200:
                        logging.info(f"订单 {order_id} 数据上传成功")
                        success_orders.append(order_id)
                    else:
                        logging.error(f"订单 {order_id} 数据上传失败，状态码: {response.status_code}, 响应内容: {response.text[:500]}...")
                        failed_orders.append(order_id)
                else:
                    logging.warning(f"订单 {order_id} 的聊天记录为空，跳过处理")
                    failed_orders.append(order_id)
            except json.JSONDecodeError as e:
                logging.error(f"订单 {order_id} JSON 解析错误: {e}")
                failed_orders.append(order_id)
        except Exception as e:
            logging.error(f"订单 {order_id} 处理失败: {str(e)}")
            failed_orders.append(order_id)
        if progress_callback:
            progress_callback(index + 1, total_orders)
    return success_orders, failed_orders

# ====================== Web & 前端 ======================
app = Flask(__name__)

progress_data = {
    "total": 0,
    "processed": 0,
    "success_orders": [],
    "failed_orders": [],
    "completed": False
}
progress_lock = threading.Lock()

HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>合规测试 - 订单上传</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .result-list { margin-top: 20px; }
        .success, .failure { list-style-type: disc; margin-left: 20px; color: green; }
        .failure { color: red; }
        button[disabled] { background-color: #ccc; cursor: not-allowed; }
        progress { width: 100%; height: 20px; }
    </style>
</head>
<body>
    <h1>合规测试 - 批量上传订单</h1>
    <form id="uploadForm">
        <label for="order_ids">请输入最多 10 个订单号（用逗号分隔）:</label><br>
        <textarea id="order_ids" name="order_ids" rows="5" cols="50" placeholder="例如：12345,67890,..." required></textarea><br>
        <button type="submit" id="submitButton">上传</button>
    </form>
    <div id="progressContainer" style="display: none; margin-top: 20px;">
        <p>处理进度：<span id="progressText">0%</span></p>
        <progress id="progressBar" value="0" max="100"></progress>
    </div>
    <div class="result-list" id="resultList" style="display: none;">
        <p>结果：</p>
        <ul class="success">
            <li>成功上传的订单: <span id="successOrders">无</span></li>
        </ul>
        <ul class="failure">
            <li>失败的订单: <span id="failedOrders">无</span></li>
        </ul>
    </div>
    <script>
        let intervalId = null;
        document.getElementById("uploadForm").addEventListener("submit", function(event) {
            event.preventDefault();
            document.getElementById("progressContainer").style.display = "block";
            document.getElementById("submitButton").disabled = true;
            const orderIdsInput = document.getElementById("order_ids").value;
            if (!orderIdsInput.trim()) {
                alert("订单号不能为空！");
                return;
            }
            fetch("/process-orders", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ order_ids: orderIdsInput })
            }).then(response => response.json())
              .then(data => {
                  if (data.status === "processing") {
                      intervalId = setInterval(fetchProgress, 500);
                  } else if (data.status === "error") {
                      alert(data.message || "发生错误");
                      document.getElementById("submitButton").disabled = false;
                      document.getElementById("progressContainer").style.display = "none";
                  }
              });
        });
        function fetchProgress() {
            fetch("/get-progress")
                .then(response => response.json())
                .then(data => {
                    const { total, processed, success_orders, failed_orders, completed } = data;
                    const progressPercent = total ? Math.round((processed / total) * 100) : 0;
                    document.getElementById("progressBar").value = progressPercent;
                    document.getElementById("progressText").innerText = `${progressPercent}%`;
                    if (completed) {
                        clearInterval(intervalId);
                        document.getElementById("resultList").style.display = "block";
                        document.getElementById("successOrders").innerText = success_orders.length ? success_orders.join(", ") : "无";
                        document.getElementById("failedOrders").innerText = failed_orders.length ? failed_orders.join(", ") : "无";
                        document.getElementById("submitButton").disabled = false;
                    }
                });
        }
    </script>
</body>
</html>
'''

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/process-orders", methods=["POST"])
def process_orders():
    order_ids_input = request.json.get("order_ids")
    if not order_ids_input:
        return jsonify({"status": "error", "message": "订单号不能为空"}), 400
    order_ids = [oid.strip() for oid in order_ids_input.split(",") if oid.strip()]
    if len(order_ids) == 0:
        return jsonify({"status": "error", "message": "请至少输入 1 个订单号"}), 400
    if len(order_ids) > 10:
        return jsonify({"status": "error", "message": "最多只能输入 10 个订单号"}), 400
    with progress_lock:
        progress_data.update({
            "total": len(order_ids),
            "processed": 0,
            "success_orders": [],
            "failed_orders": [],
            "completed": False
        })
    def background_task(order_list):
        success_orders, failed_orders = upload_multiple_orders(
            order_list,
            progress_callback=lambda processed, total=None: update_progress(processed)
        )
        with progress_lock:
            progress_data["success_orders"] = success_orders
            progress_data["failed_orders"] = failed_orders
            progress_data["completed"] = True
    threading.Thread(target=background_task, args=(order_ids,), daemon=True).start()
    return jsonify({"status": "processing"})

@app.route("/get-progress", methods=["GET"])
def get_progress():
    with progress_lock:
        return jsonify(progress_data)

def update_progress(processed):
    with progress_lock:
        progress_data["processed"] = processed

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)