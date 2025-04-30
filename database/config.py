import os

from dotenv import load_dotenv

load_dotenv()

# 可以通过环境变量来动态配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 8000)),  # 如果你使用了 5433 端口
    "user": os.getenv("DB_USER", "rotator"),
    "password": os.getenv("DB_PASSWORD", "sdf3sjdkfds232jfklsle234"),
    "dbname": os.getenv("DB_NAME", "rotator_database"),
}

TOR_HS_FPATH = os.getenv("TOR_HS_FPATH")
TOR_HS_RPATH = os.getenv("TOR_HS_RPATH")
TOR_TORRC = os.getenv("TOR_TORRC")
TOR_SERVER = os.getenv("TOR_SERVER")
TOR_HS_PS = os.getenv("TOR_HS_PS", "rotatorpsw")

ROTATOR_TIME = int(os.getenv("ROTATOR_TIME", 7 * 60))
EXPIRES_AT = int(os.getenv("EXPIRES_AT", 60 * 60))
CHECK_TIME = int(os.getenv("CHECK_TIME", 12 * 60 * 60))
