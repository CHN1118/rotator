
def create_fixed_onion_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixed_onion (
            id SERIAL PRIMARY KEY,
            address TEXT UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            deactivated_at TIMESTAMP NULL,
            cleaned_at TIMESTAMP NULL,  -- 🆕 新增字段，标记是否已清理
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

