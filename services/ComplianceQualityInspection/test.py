import sys
import os
import time
import json
import hashlib
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import AES
import base64
import urllib3
from datetime import datetime, timedelta
import configparser
import logging

# 定义公共路径
BASE_PATH = r'C:\Users\Administrator\Desktop\services\ComplianceQualityInspection\log'

# 添加 function.py 所在目录到系统路径
sys.path.append(BASE_PATH)

# 导入自定义函数
from function import rsa_encrypt, aes_decrypt, validate_and_parse_json, generate_conversation_id, replace_with_conversation_id, fetch_and_decrypt_chat_log, fetch_and_decrypt_order_list, upload_to_crm, aes_en, aes_de

# 忽略警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 设置日志配置（绝对路径）
LOG_FILE = os.path.join(BASE_PATH, 'upload.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 读取配置文件内的各参数（绝对路径）
CONFIG_FILE = os.path.join(BASE_PATH, 'config.ini')
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 验证配置文件中的必要参数
required_api_keys = ['url_get_chat_log', 'url_get_order_list', 'url_submit', 'appsecret', 'agent', 'appid', 'preprocess']
required_key_paths = ['public_key_path', 'private_key_path']

missing_api_keys = [key for key in required_api_keys if not config.has_option('API', key)]
missing_key_paths = [key for key in required_key_paths if not config.has_option('Keys', key)]

if missing_api_keys or missing_key_paths:
    error_message = ""
    if missing_api_keys:
        error_message += f"API 配置缺少以下参数: {', '.join(missing_api_keys)}\n"
    if missing_key_paths:
        error_message += f"密钥路径配置缺少以下参数: {', '.join(missing_key_paths)}"
    logging.error(error_message.strip())
    sys.exit(1)

# 读取 API 配置
url_get_chat_log = config.get('API', 'url_get_chat_log')
url_get_order_list = config.get('API', 'url_get_order_list')
url_submit = config.get('API', 'url_submit_formal')
appsecret = config.get('API', 'appsecret')
agent = config.get('API', 'agent')
appid = config.get('API', 'appid')
preprocess = int(config.get('API', 'preprocess'))  # preprocess=0 是不处理图片和语音，preprocess=1 是处理图片和语音
aes_DEFAULT_KEY = config.get('API', 'aes_DEFAULT_KEY')

# 使用 BASE_PATH 重写密钥路径
PUBLIC_KEY_FILENAME = 'public_key.pem'  # 公钥文件名
PRIVATE_KEY_FILENAME = 'private_key.pem'  # 私钥文件名

public_key_path = os.path.join(BASE_PATH, PUBLIC_KEY_FILENAME)
private_key_path = os.path.join(BASE_PATH, PRIVATE_KEY_FILENAME)

# 检查密钥文件是否存在
if not os.path.exists(public_key_path):
    logging.error(f"公钥文件未找到: {public_key_path}")
    sys.exit(1)
if not os.path.exists(private_key_path):
    logging.error(f"私钥文件未找到: {private_key_path}")
    sys.exit(1)

# 定义开始和结束时间
# 获取当前时间
now = datetime.now()
# 计算1小时前的时间
two_hours_ago = now - timedelta(hours=1)
# 格式化为 'YYYY-MM-DD HH:MM:SS'
start_time_string = two_hours_ago.strftime("%Y-%m-%d %H:%M:%S")  # 1小时前的时间
end_time_string = now.strftime("%Y-%m-%d %H:%M:%S")              # 当前时间

# 开始时间（手动设置）
start_time_string = "2025-06-29 09:00:00"
# 结束时间（手动设置）
end_time_string = "2025-06-29 12:00:00"

# 记录任务开始时间
task_start_time = datetime.now()
logging.info("任务开始时间: {}".format(task_start_time.strftime('%Y-%m-%d %H:%M:%S')))

# 初始化统计变量
total_orders = 0
successful_orders = 0
failed_orders = 0
skipped_orders = 0

# 获取订单数据
range = 'all'   # all获取全量, only_not_pass仅未通过订单
try:
    order_number_list = fetch_and_decrypt_order_list(
        start_time_string, end_time_string, range, public_key_path, private_key_path,
        url_get_order_list, appsecret, agent, appid
    )
except Exception as e:
    logging.error(f"获取订单列表失败: {str(e)}")
    sys.exit(1)

# 如果订单列表为空，直接结束任务
if not order_number_list:
    logging.warning("本次任务未获取到任何订单数据，任务提前结束")
    task_end_time = datetime.now()
    logging.info("任务结束时间: {}".format(task_end_time.strftime('%Y-%m-%d %H:%M:%S')))
    task_duration = task_end_time - task_start_time
    logging.info(f"任务总运行时间: {task_duration}")
    logging.info(f"订单总数: {total_orders}")
    logging.info(f"成功处理的订单数: {successful_orders}")
    logging.info(f"失败的订单数: {failed_orders}")
    logging.info(f"跳过的订单数: {skipped_orders}")
    sys.exit(0)

# 统计订单总数
total_orders = len(order_number_list)
logging.info(f"本次任务共获取到 {total_orders} 个订单")

# 按订单列表数据获取聊天记录，并上传阿里AI接口
headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'Content-Type': 'application/json'
}

# 循环处理每个订单
for order_id in order_number_list:

    time.sleep(0.02)

    order_id = str(order_id)
    
    # 调用封装的函数获取解密结果
    try:
        decrypted_result = fetch_and_decrypt_chat_log(order_id, public_key_path, private_key_path, url_get_chat_log, appsecret, agent, appid)
        
        # 验证并解析解密结果
        try:
            json_content = replace_with_conversation_id(validate_and_parse_json(decrypted_result))
            if json_content != []:
                if isinstance(json_content[0], dict):
                    json_content[0]['preprocess'] = preprocess
                    
                    # 使用 AES 加密数据
                    plain_text = json.dumps(json_content[0])  # 将 JSON 数据转换为字符串
                    encrypted_data = aes_en(plain_text, aes_DEFAULT_KEY)  # 使用 AES 加密
                    
                    if not encrypted_data:
                        logging.error(f"订单 {order_id} 数据加密失败，跳过处理")
                        skipped_orders += 1
                        continue
                    
                    
                    # 调用阿里 AI 接口上传加密数据
                    response = requests.request(
                        "POST", 
                        url_submit, 
                        headers=headers, 
                        data= json.dumps({"data":encrypted_data}) , 
                        timeout=30
                    )
                    
                    # 检查响应状态码
                    if response.status_code == 200:
                        successful_orders += 1
                        # logging.info(f"订单 {order_id} 数据上传成功")
                    else:
                        failed_orders += 1
                        logging.error(f"订单 {order_id} 数据上传失败，状态码: {response.status_code}, 响应内容: {response.text[:500]}...")
                else:
                    logging.error(f"订单 {order_id} 的 JSON 数据格式不正确，无法设置 preprocess 参数")
                    skipped_orders += 1
                    continue
                
            else:
                skipped_orders += 1
                logging.warning(f"订单 {order_id} 的聊天记录为空，跳过处理")
                continue

        except json.JSONDecodeError as e:
            failed_orders += 1
            logging.error(f"订单 {order_id} JSON 解析错误: {e}")

    except Exception as e:
        failed_orders += 1
        logging.error(f"订单 {order_id} 处理失败: {str(e)}")
        continue

# 记录任务结束时间
task_end_time = datetime.now()
logging.info("任务结束时间: {}".format(task_end_time.strftime('%Y-%m-%d %H:%M:%S')))

# 计算任务运行时间
task_duration = task_end_time - task_start_time
logging.info(f"任务总运行时间: {task_duration}")

# 统计结果
logging.info(f"订单总数: {total_orders}")
logging.info(f"成功处理的订单数: {successful_orders}")
logging.info(f"失败的订单数: {failed_orders}")
logging.info(f"跳过的订单数: {skipped_orders}")