import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, session, flash, g
import requests
import json
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from datetime import datetime, timedelta
import random
from config import API_URL, API_TOKEN, MCP_SEE_URL, MODEL_SERVER_PLATFORM
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import sqlalchemy.exc

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')  # 用于session加密
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# SSE 客户端列表，用于实时推送更新
# 注意：这在多进程部署下不适用，仅适用于单进程开发环境
clients = []

async def sse_event_stream():
    queue = asyncio.Queue()
    clients.append(queue)
    try:
        while True:
            message = await queue.get()
            yield f"data: {json.dumps(message)}\n\n"
    except asyncio.CancelledError:
        # 客户端断开连接
        pass
    finally:
        clients.remove(queue)

# 用户模型
class User(db.Model):
    __tablename__ = 'users' # 明确指定表名
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin', 'user', 'guest'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 帖子模型
class Post(db.Model):
    __tablename__ = 'posts' # 明确指定表名
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
print("Post模型已定义")

# 课程模型
class Course(db.Model):
    __tablename__ = 'courses' # 明确指定表名
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    course_time = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    color = db.Column(db.String(7), default='#007bff')
    day = db.Column(db.String(50), nullable=True)    # 新增：周几
    period = db.Column(db.String(50), nullable=True) # 新增：第几节
    weeks = db.Column(db.String(100), nullable=True) # 新增：周次
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    owner = db.relationship('User', backref=db.backref('courses', lazy=True))
print("Course模型已定义")

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 管理员权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = db.session.get(User, session['user_id']) # 使用 db.session.get
        if not user or user.role != 'admin':
            flash('需要管理员权限')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# 初始化数据库
# init_db() # 移除此行

# Helper to get current user from session
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id) # 使用 db.session.get
        if user: # and user.is_active:
            return user
    return {'role': 'guest', 'is_active': True} # Default guest user

@app.before_request
def before_request():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id) # 使用 db.session.get
        if user: # and user.is_active: # 再次检查用户是否存在且激活
            g.user = user
        else:
            # 如果session中的user_id无效或用户不存在，则清除session并设为guest
            session.pop('user_id', None)
            session.pop('username', None)
            session.pop('role', None)
            g.user = {'role': 'guest', 'is_active': True} # 默认guest用户
    else:
        g.user = {'role': 'guest', 'is_active': True} # 默认guest用户

@app.route('/')
def home():
    return render_template('home.html', current_user=get_current_user())

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', current_user=get_current_user())

@app.route('/tieba')
def tieba():
    return render_template('tieba.html', current_user=get_current_user())

@app.route('/timetable')
def timetable():
    return render_template('timetable.html', current_user=get_current_user())

@app.route('/config')
@admin_required
def config():
    return render_template('config.html', current_user=get_current_user())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='用户名已存在', current_user=get_current_user())

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    return render_template('register.html', current_user=get_current_user())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return render_template('login.html', error='无效的用户名或密码', current_user=get_current_user())
        
        if not user.is_active:
            return render_template('login.html', error='该账户已被禁用，请联系管理员', current_user=get_current_user())

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        # Update last_login time
        user.last_login = datetime.utcnow()
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('login.html', current_user=get_current_user())

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home'))

@app.route('/sse/updates')
async def sse_updates():
    print("进入 sse_updates 路由")
    return Response(sse_event_stream(), mimetype='text/event-stream')

# Helper function to send SSE events
def send_sse_update(event_type, data=None):
    message = {'event': event_type, 'data': data}
    for queue in clients:
        # 使用 put_nowait 防止阻塞，如果队列已满则忽略
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull: # type: ignore
            print("Client queue is full, skipping update.")

# 贴吧API路由
@app.route('/api/posts', methods=['GET'])
def get_posts():
    print("进入 get_posts 路由")
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username if post.author else '匿名',
        'created_at': post.created_at.isoformat(),
        'likes': post.likes
    } for post in posts])

@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': '请先登录'}), 403
    
    data = request.json
    user = db.session.get(User, session['user_id']) # 使用 db.session.get
    
    post = Post(
        title=data['title'],
        content=data['content'],
        user_id=user.id # 修正：赋值给user_id
    )
    db.session.add(post)
    db.session.commit()
    # 发送 SSE 更新通知
    send_sse_update('new_post')
    return jsonify({'success': True, 'message': '帖子创建成功'})

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    user = db.session.get(User, session['user_id'])
    if not user or not user.is_active:
        return jsonify({'success': False, 'error': '请先登录或激活账户'}), 403

    post = db.session.get(Post, post_id)
    if post:
        post.likes += 1
        db.session.commit()
        # 发送 SSE 更新通知
        send_sse_update('post_liked', {'post_id': post_id})
        return jsonify({'success': True, 'likes': post.likes})
    return jsonify({'success': False, 'error': '点赞失败'}), 400

@app.route('/api/hot-topics', methods=['GET'])
def get_hot_topics():
    topics = Post.query.with_entities(Post.title, db.func.count(Post.id)).group_by(Post.title).order_by(db.func.count(Post.id).desc()).limit(5).all()
    return jsonify([{'title': t[0], 'count': t[1]} for t in topics])

# 课表API路由
@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    courses = Course.query.order_by(Course.course_name).all()
    return jsonify([{
        'id': course.id,
        'name': course.course_name,
        'teacher': course.course_time,
        'location': course.location,
        'color': course.color,
        'day': course.day,     # 新增：返回周几
        'period': course.period, # 新增：返回第几节
        'weeks': course.weeks  # 新增：返回周次
    } for course in courses])

@app.route('/api/timetable', methods=['POST'])
@login_required
def add_course():
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': '请先登录'}), 403
    
    data = request.json
    user = db.session.get(User, session['user_id'])

    course = Course(
        course_name=data['name'],
        course_time=data['teacher'],
        location=data['location'],
        color=data['color'],
        day=data.get('day'),      # 新增：获取周几
        period=data.get('period'),  # 新增：获取第几节
        weeks=data.get('weeks'),   # 新增：获取周次
        user_id=user.id
    )
    db.session.add(course)
    db.session.commit()
    send_sse_update('new_course', data)
    return jsonify({'success': True, 'message': '课程添加成功'})

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
@login_required
def delete_course(course_id):
    user = db.session.get(User, session['user_id'])
    if not user or not user.is_active:
        return jsonify({'success': False, 'error': '请先登录或激活账户'}), 403

    course = db.session.get(Course, course_id)
    if course:
        # 检查权限
        if session.get('user_id') != course.user_id and not (user and user.role == 'admin'):
            return jsonify({'success': False, 'error': '没有权限删除此课程'}), 403

        db.session.delete(course)
        db.session.commit()
        send_sse_update('delete_course', {'id': course_id})
        return jsonify({'success': True, 'message': '课程删除成功'})
    return jsonify({'success': False, 'error': '删除失败'}), 400

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = db.session.get(Course, course_id)
    if course:
        return jsonify({
            'id': course.id,
            'name': course.course_name,
            'teacher': course.course_time,
            'location': course.location,
            'color': course.color
        })
    return jsonify({'error': '课程未找到'}), 404

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
@login_required
def update_course(course_id):
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': '请先登录'}), 403
    
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'error': '课程未找到'}), 404
    
    # 检查权限
    user = db.session.get(User, session['user_id'])
    if session.get('user_id') != course.user_id and not (user and user.role == 'admin'):
        return jsonify({'success': False, 'error': '没有权限修改此课程'}), 403

    data = request.json
    course.course_name = data['name']
    course.course_time = data['teacher']
    course.location = data['location']
    course.color = data['color']
    course.day = data.get('day')      # 新增：更新周几
    course.period = data.get('period')  # 新增：更新第几节
    course.weeks = data.get('weeks')   # 新增：更新周次
    
    db.session.commit()
    send_sse_update('update_course', {'id': course.id, 'name': course.course_name, 'teacher': course.course_time, 'location': course.location, 'color': course.color, 'day': course.day, 'period': course.period, 'weeks': course.weeks})
    return jsonify({'success': True, 'message': '课程更新成功'})

@app.route('/api/timetable/export/csv', methods=['GET'])
def export_timetable_csv():
    import csv
    from io import StringIO

    si = StringIO()
    cw = csv.writer(si)

    # Write header
    cw.writerow(['ID', '课程名称', '教师', '地点', '周几', '第几节', '周次', '颜色'])

    courses = Course.query.order_by(Course.course_name).all()
    for course in courses:
        cw.writerow([
            course.id,
            course.course_name,
            course.course_time,
            course.location,
            course.day,     # 新增：导出周几
            course.period,  # 新增：导出第几节
            course.weeks,   # 新增：导出周次
            course.color
        ])

    output = si.getvalue()
    response = Response(output, mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=timetable.csv"
    return response

@app.route("/config", methods=["POST"])
async def save_config():
    data = request.json
    try:
        model_server_platform = MODEL_SERVER_PLATFORM[data["model-server-platform"]]
        api_token = API_TOKEN
        model = "Qwen/Qwen3-8B"
        choose_mcp_server_type = "sse"
        sse_server_url = MCP_SEE_URL
    except:
        return jsonify({"msg": "缺少必要参数"}), 400

    try:
        async with sse_client(url=sse_server_url) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
    except:
        return jsonify({"msg":"连接失败，检查你的设置"}), 400
        
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    payload = {
        "model": model,
        "messages": [{"role":"user","content":"这只是一个测试对话是否可以使用，不需要回复我！"}],
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
    }
    api_response = requests.post(
        model_server_platform,
        json=payload,
        headers=headers,
    )
    if api_response.status_code == 401:
        return jsonify({"msg": "token错误"}), 401
    elif api_response.status_code == 400:
        return jsonify({"msg": api_response.json()["message"]}), 401
    elif api_response.status_code == 404:
        return jsonify({"msg": "404 page not found"}), 401
    return jsonify({
        "current_setting": {
            "model_server_platform": model_server_platform,
            "api_token": api_token,
            "model": model,
            "choose_mcp_server_type": choose_mcp_server_type,
            "sse_server_url": sse_server_url,
        }
    })

@app.route('/api/chat', methods=['POST'])
async def api_chat():
    data = request.json
    try:
        messages = data.get('messages', [])
        open_mcp = data.get("open_mcp", True)
        if open_mcp:
            sse_server_url = data.get("sse-server-url", MCP_SEE_URL)
        apiToken = data.get("apiToken", API_TOKEN)
        model = data.get("model", "Qwen/Qwen3-8B")
    except:
        return jsonify({"msg": "错误的配置"}), 400
    if open_mcp:
        return await mcp_api_chat(messages, apiToken, model, sse_server_url)
    else:
        return normal_api_chat(messages, apiToken, model)

async def mcp_api_chat(messages, apiToken, model, sse_server_url):
    async with sse_client(url=sse_server_url) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            tools_response = await session.list_tools()
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 50,
                "frequency_penalty": 0.5,
                "n": 1,
                "response_format": {"type": "text"},
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "description": item.description,
                            "name": item.name,
                            "parameters": item.inputSchema,
                            "strict": False
                        }
                    }
                    for item in tools_response.tools
                ]
            }

            headers = {
                "Authorization": f"Bearer {apiToken}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            }

            api_response = requests.post(
                API_URL,
                json=payload,
                headers=headers,
            )
            try:
                tool_calls = api_response.json()["choices"][0]["message"]["tool_calls"]
            except:
                tool_calls = []
            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                result = await session.call_tool(tool_name, tool_args)
                print(tool_name, tool_args, result)
                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args)
                            }
                        }
                    ]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": str(result.content)
                })

            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 50,
                "frequency_penalty": 0.5,
                "n": 1,
                "response_format": {"type": "text"},
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "description": item.description,
                            "name": item.name,
                            "parameters": item.inputSchema,
                            "strict": False
                        }
                    }
                    for item in tools_response.tools
                ]
            }
            api_response = requests.post(
                API_URL,
                json=payload,
                headers=headers,
                stream=True
            )

            def generate():
                for chunk in api_response.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk

            return Response(generate(), content_type='text/event-stream')

def normal_api_chat(messages, apiToken, model):
    headers = {
        "Authorization": f"Bearer {apiToken}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
    }
    api_response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        stream=True
    )

    def generate():
        for chunk in api_response.iter_content(chunk_size=None):
            if chunk:
                yield chunk

    return Response(generate(), content_type='text/event-stream')

# 辅助函数
def is_admin():
    if 'user_id' not in session:
        return False
    user = User.query.get(session['user_id'])
    return user and user.role == 'admin'

if __name__ == '__main__':
    with app.app_context():
        db.drop_all() # 强制删除所有表
        db.create_all() # 在应用上下文中创建所有表
        # 检查并创建默认管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(username='admin', role='admin', is_active=True)
            admin.set_password('adminpassword') # 设置管理员密码
            db.session.add(admin)
            try:
                db.session.commit()
                print("默认管理员用户'admin'已创建，密码为'adminpassword'")
            except Exception as e:
                db.session.rollback()
                print(f"创建管理员用户失败: {e}")
                if isinstance(e, sqlalchemy.exc.DataError):
                    print(f"生成的密码哈希长度: {len(admin.password_hash)}")
                    print(f"密码哈希内容: {admin.password_hash}")
                print("请手动创建管理员用户或检查数据库结构")

    # 使用 Uvicorn 运行 Flask 应用
    asgi_app = WsgiToAsgi(app)
    uvicorn.run(asgi_app, host='127.0.0.1', port=8000)
