import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '123456'),
    'database': os.getenv('MYSQL_DATABASE', 'mcp_server'),
    'charset': 'utf8mb4'
}

# API配置
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_TOKEN = "sk-pvibdzgjvaiqwzuikkltbfupjqewalvptylzabtjkvnujtry"
MCP_SEE_URL = "http://localhost:9000/sse"
MODEL_SERVER_PLATFORM = {
    "硅基流动": "https://api.siliconflow.cn/v1/chat/completions",
} 