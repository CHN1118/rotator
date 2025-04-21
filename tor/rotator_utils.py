from stem.control import Controller
import os
import time
from database.connection import with_cursor
from database.config import TOR_HS_PS

def create_rotator_onion():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password=TOR_HS_PS)

        # 创建 ephemeral onion 地址监听本地 8080 端口
        result = controller.create_ephemeral_hidden_service({80: 8080}, await_publication=True)

        address = result.service_id + ".onion"
        private_key = result.private_key
        timestamp = int(time.time())
        description = f"ephemeral_{timestamp}"

        print("✅ 创建 onion 成功:", address)

        # 写入数据库
        def insert(cursor):
            cursor.execute("""
                INSERT INTO rotating_onion (address, private_key, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (address) DO UPDATE SET
                    updated_at = CURRENT_TIMESTAMP;
            """, (address, private_key, description))
        with_cursor(insert)

        return {
            "address": address,
            "private_key": private_key,
            "service_id": result.service_id,
        }
