import os
# import datetime
from database.config import TOR_HS_PATH

def scan_onion_dirs(cursor, base_dir=TOR_HS_PATH, table='fixed_onion'):
    count = 0
    for subdir in os.listdir(base_dir): # 遍历所有子目录
        full_path = os.path.join(base_dir, subdir, 'hostname') # 拼接子目录路径和文件名
        if not os.path.isfile(full_path): # 跳过非文件
            continue
        try:
            with open(full_path, 'r') as f: # 读取文件内容
                onion = f.read().strip() # 去掉空格和换行符
                if onion:
                    cursor.execute(f"""
                        INSERT INTO {table} (address, description)
                        VALUES (%s, %s)
                        ON CONFLICT (address) DO UPDATE SET
                            updated_at = CURRENT_TIMESTAMP;
                    """, (onion, subdir))
                    print(f"✅ 插入 {onion} (描述: {subdir})")
                    count += 1
        except Exception as e:
            print(f"❌ 读取 {full_path} 失败: {e}")
    print(f"🔚 共处理 {count} 个 onion 地址")
