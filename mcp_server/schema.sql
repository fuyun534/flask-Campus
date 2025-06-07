-- 创建贴吧帖子表
CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 创建贴吧评论表
CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- 创建课表表
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    teacher VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    day INT NOT NULL,  -- 1-7 表示周一到周日
    period INT NOT NULL,  -- 1-8 表示第几节课
    weeks VARCHAR(50) NOT NULL,  -- 例如：1-16周
    color VARCHAR(20) DEFAULT '#FFB6C1',  -- 课程颜色
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 创建 users 表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role ENUM('guest', 'user', 'admin') DEFAULT 'user', -- guest: 游客, user: 普通用户, admin: 管理员
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE, -- 用于封禁/解封用户
    last_login DATETIME -- 记录最后登录时间，用于统计
);

-- 修改 posts 表，添加 user_id 外键
-- 注意：如果 posts 表已有数据且 author 字段不为空，需要先处理数据或允许 author 为 NULL
ALTER TABLE posts
ADD COLUMN user_id INT,
ADD FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

-- 修改 courses 表，添加 user_id 外键
-- 注意：如果 courses 表已有数据，需要先处理数据
ALTER TABLE courses
ADD COLUMN user_id INT,
ADD FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL; 