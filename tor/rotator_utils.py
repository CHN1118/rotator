import os
import hashlib
import secrets
import psutil
from database.config import TOR_TORRC, TOR_SERVER



# 修改 torrc 文件，动态添加新的隐藏服务
def add_hidden_service(new_hidden_service_dir, port, backend_ip, backend_port):
    with open(TOR_TORRC, 'a') as f:
        f.write(f"\nHiddenServiceDir {new_hidden_service_dir}\n")
        f.write(f"HiddenServicePort {port} {backend_ip}:{backend_port}\n")
        print("✅ sdfsdfd")
    pid = find_tor_pid()
    # 发送 SIGHUP 信号给 Tor 进程，重新加载配置
    os.system(f"kill -HUP {pid}")

# 使用示例

def find_tor_pid(tor_path=TOR_SERVER):
    for proc in psutil.process_iter(['pid', 'exe', 'name']):
        try:
            if proc.info['exe'] == tor_path:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def generate_irreversible_string(length=10, input_data=None):
    # 如果未提供输入数据，则生成随机盐值
    if input_data is None:
        input_data = secrets.token_hex(16)  # 32字符的随机字符串

    # 使用 SHA-256 哈希生成不可逆字符串
    hash_obj = hashlib.sha256(input_data.encode())
    hash_hex = hash_obj.hexdigest()  # 64字符的十六进制哈希值

    # 截取指定位数（若超过哈希长度则循环填充）
    return hash_hex[:length] if length <= 64 else (hash_hex * (length // 64 + 1))[:length]
