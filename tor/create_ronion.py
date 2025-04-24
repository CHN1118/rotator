import os
import time
from datetime import datetime, timedelta
from database.config import TOR_HS_RPATH, EXPIRES_AT, TOR_TORRC
from database.connection import get_connection
from tor.rotator_utils import generate_irreversible_string, add_hidden_service


def create_ronion():
    result = generate_irreversible_string(12) # 生成随机字符串
    file_name = f"r_o{result}"
    onion_path = os.path.join(TOR_HS_RPATH, file_name) # 生成隐藏服务路径
    add_hidden_service(onion_path, 80, '127.0.0.1', 8080) # 添加隐藏服务
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
        pid = os.popen("pgrep -f tor").read().strip()
        if pid:
            os.system(f"kill -HUP {pid}")
            print("📢 已通知 Tor 重载配置")
        else:
            print("❌ 未找到 Tor 进程")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 所有过期服务已处理完毕")