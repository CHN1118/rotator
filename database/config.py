import os

# 可以通过环境变量来动态配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 8000)),  # 如果你使用了 5433 端口
    "user": os.getenv("DB_USER", "rotator"),
    "password": os.getenv("DB_PASSWORD", "sdf3sjdkfds232jfklsle234"),
    "dbname": os.getenv("DB_NAME", "rotator_database"),
}

TOR_HS_FPATH = "/opt/homebrew/var/lib/tor/fixed_onion"
TOR_HS_RPATH = "/opt/homebrew/var/lib/tor/rotating_onion"
TOR_TORRC = "/opt/homebrew/etc/tor/torrc"
TOR_SERVER = "/opt/homebrew/Cellar/tor/0.4.8.16/bin/tor"

TOR_HS_PS = "rotatorpsw"

# ROTATOR_TIME = 7 * 60
# 7分钟生成一个新的
ROTATOR_TIME = 14

# 过期时间为1小时
EXPIRES_AT = 30

# 清理文件时间
CHECK_TIME = 30
