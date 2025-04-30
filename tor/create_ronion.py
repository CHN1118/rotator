import os
import shutil
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv

from database.config import TOR_HS_RPATH, EXPIRES_AT, TOR_TORRC, CHECK_TIME
from database.connection import get_connection
from tor.rotator_utils import generate_irreversible_string, add_hidden_service, find_tor_pid

load_dotenv()
# 创建动态.onion
def create_ronion():
    result = generate_irreversible_string(12) # 生成随机字符串
    file_name = f"r_o{result}"
    onion_path = os.path.join(TOR_HS_RPATH, file_name) # 生成隐藏服务路径
    add_hidden_service(onion_path, 80, os.getenv("ONION_IP", "127.0.0.1"), os.getenv("ONION_PORT", "7100"))# 添加隐藏服务
    # 等待 hostname 文件生成
    hostname_file = os.path.join(onion_path, 'hostname')
    for _ in range(30):  # 最多等待 30 秒
        if os.path.exists(hostname_file):
            break
        time.sleep(1) # 等待 1 秒
    else:
        print("❌ 超时未生成 hostname 文件")
        return

    # 读取 hostname
    with open(hostname_file, 'r') as f:
        onion_address = f.read().strip()

    print(f"🌐 新地址生成: {onion_address}")

    # 写入数据库（默认1小时后过期）
    expires_at = datetime.utcnow() + timedelta(seconds=EXPIRES_AT)
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rotating_onion (address, expires_at, description)
            VALUES (%s, %s,%s)
            ON CONFLICT (address) DO NOTHING;
        """, (onion_address, expires_at, file_name))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 已存入数据库")

    return onion_address  # 可返回给调用者做记录


# 检查过期的.onion
def deactivate_expired_onions():
    now = datetime.utcnow()
    conn = get_connection()
    if not conn:
        print("❌ 数据库连接失败")
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT address, description FROM rotating_onion
        WHERE is_active = TRUE AND expires_at < %s;
    """, (now,))
    expired = cursor.fetchall()

    if not expired:
        print("✅ 没有过期的 onion 地址")
        cursor.close()
        conn.close()
        return

    # 读取 torrc 内容
    with open(TOR_TORRC, 'r') as f:
        torrc_lines = f.readlines()

    updated_lines = []
    for line in torrc_lines:
        updated_lines.append(line)

    modified = False

    for address, description in expired:
        print(f"🔍 正在处理过期地址: {address} ({description})")
        service_dir = os.path.join(TOR_HS_RPATH, description)

        # 注释掉包含该服务目录的 HiddenServiceDir 配置块
        i = 0
        while i < len(updated_lines):
            if f"HiddenServiceDir {service_dir}" in updated_lines[i]:
                print(f"📝 注释掉配置：{updated_lines[i].strip()}")
                updated_lines[i] = f"# {updated_lines[i]}"
                if i + 1 < len(updated_lines) and "HiddenServicePort" in updated_lines[i + 1]:
                    updated_lines[i + 1] = f"# {updated_lines[i + 1]}"
                modified = True
                break
            i += 1

        # 更新数据库记录
        cursor.execute("""
            UPDATE rotating_onion
            SET is_active = FALSE,
                deactivated_at = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE address = %s;
        """, (now, address))

    if modified:
        with open(TOR_TORRC, 'w') as f:
            f.writelines(updated_lines)
        print("✅ 已更新 torrc 文件")

        # 重载 tor 服务配置
        pid = find_tor_pid()
        if pid:
            os.system(f"kill -HUP {pid}")
            print("📢 已通知 Tor 重载配置")
        else:
            print("❌ 未找到 Tor 进程")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 所有过期服务已处理完毕")

def clean_fully_expired_onions():
    now = datetime.utcnow()
    conn = get_connection()
    if not conn:
        print("❌ 数据库连接失败")
        return

    cursor = conn.cursor()
    # 查询已过期12小时且未清理的
    cursor.execute("""
        SELECT id, address, description FROM rotating_onion
        WHERE expires_at < %s AND cleaned_at IS NULL;
    """, (now - timedelta(seconds=CHECK_TIME),))
    expired = cursor.fetchall()

    if not expired:
        print("🧹 没有需要清理的 onion 地址")
        cursor.close()
        conn.close()
        return

    # 读取 torrc 内容
    with open(TOR_TORRC, 'r') as f:
        torrc_lines = f.readlines()

    updated_lines = list(torrc_lines)
    modified = False

    for onion_id, address, description in expired:
        service_dir = os.path.join(TOR_HS_RPATH, description)
        print(f"🧹 正在清理服务 {address} ({description})")

        # 删除 torrc 中的相关配置
        i = 0
        while i < len(updated_lines):
            if f"HiddenServiceDir {service_dir}" in updated_lines[i]:
                print(f"🧾 删除配置：{updated_lines[i].strip()}")
                del updated_lines[i-1:i+2]
                modified = True
                continue  # 不增加 i，因为列表缩短了
            i += 1

        # 删除本地隐藏服务目录
        if os.path.exists(service_dir):
            shutil.rmtree(service_dir)
            print(f"🗑️ 已删除目录 {service_dir}")

        # 更新数据库记录为已清理
        cursor.execute("""
            UPDATE rotating_onion
            SET cleaned_at = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (now, onion_id))

    # 写回 torrc
    if modified:
        with open(TOR_TORRC, 'w') as f:
            f.writelines(updated_lines)
        print("✅ torrc 文件已更新")

        # 通知 Tor 重载配置
        pid = find_tor_pid()
        if pid:
            os.system(f"kill -HUP {pid}")
            print("📢 已通知 Tor 重载配置")
        else:
            print("❌ Tor 进程未找到")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 清理任务完成")
