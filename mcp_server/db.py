import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """执行SQL查询
    
    Args:
        query (str): SQL查询语句
        params (tuple, optional): 查询参数
        fetch (bool): 是否获取结果
        
    Returns:
        list: 查询结果列表（如果fetch=True）
        int: 影响的行数（如果fetch=False）
    """
    connection = get_db_connection()
    if not connection:
        return None
        
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.rowcount
            
        cursor.close()
        return result
    except Error as e:
        print(f"执行查询错误: {e}")
        return None
    finally:
        connection.close()

def init_db():
    """初始化数据库表"""
    with open('schema.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
        
    connection = get_db_connection()
    if not connection:
        return False
        
    try:
        cursor = connection.cursor()
        for statement in sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        connection.commit()
        return True
    except Error as e:
        print(f"初始化数据库错误: {e}")
        return False
    finally:
        cursor.close()
        connection.close() 