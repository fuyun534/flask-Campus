import pymysql
import os

# 从环境变量读取数据库配置
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '123456')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'mcp_server')

def get_foreign_key_names_referencing_table(cursor, table_name, referenced_table_name):
    """获取表中所有引用指定表的外国键名称"""
    foreign_key_names = []
    cursor.execute(f"SHOW CREATE TABLE {table_name}")
    create_table_sql = cursor.fetchone()[1]
    lines = create_table_sql.split('\n')
    for line in lines:
        if f'FOREIGN KEY (`user_id`) REFERENCES `{referenced_table_name}`' in line:
            if 'CONSTRAINT' in line:
                fk_name_part = line.split('CONSTRAINT')[1].split('FOREIGN KEY')[0].strip().strip('`')
                foreign_key_names.append(fk_name_part)
    return foreign_key_names

def run_sqls():
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset='utf8mb4'
    )
    try:
        with conn.cursor() as cursor:
            # 1. 关闭外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            print("关闭外键检查成功")

            # 2. 删除所有相关的表 (如果存在) - 这将删除所有数据
            for table_name in ['posts', 'courses', 'users']:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    print(f"如果存在，删除表 {table_name} 成功")
                except Exception as e:
                    print(f"删除表 {table_name} 失败: {e}")

            # 3. 创建 users 表 (确保长度正确)
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password_hash VARCHAR(512) NOT NULL,
                    role ENUM('guest', 'user', 'admin') DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_login DATETIME
                )
            """)
            print("创建users表成功")

            # 4. 创建 posts 表
            cursor.execute("""
                CREATE TABLE posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    likes INT DEFAULT 0,
                    user_id INT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            print("创建posts表成功")

            # 5. 创建 courses 表
            cursor.execute("""
                CREATE TABLE courses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    course_name VARCHAR(255) NOT NULL,
                    course_time VARCHAR(255) NOT NULL,
                    location VARCHAR(255),
                    color VARCHAR(7) DEFAULT '#007bff',
                    day VARCHAR(50),
                    period VARCHAR(50),
                    weeks VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id INT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            print("创建courses表成功")
            
            # 6. 开启外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            print("开启外键检查成功")

        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    run_sqls()
    print("数据库结构修复完成！") 