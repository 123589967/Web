from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许跨域请求

# ====================== 数据库配置（只改这里！）======================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",           # 数据库用户名（一般是root）
    "password": "Rao@20071115",  # 改成你自己的 MySQL 密码
    "database": "love_memories", # 数据库名
    "charset": "utf8mb4"
}

# 连接数据库
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# ====================== 页面路由 ======================
# 访问首页 = 登录页
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 访问主页
@app.route('/Home.html')
def home():
    return send_from_directory('.', 'Home.html')

# 静态资源（图片、音频等）
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# ====================== 登录接口 ======================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"code": -1, "msg": "请输入账号和密码"})

    # 查询数据库
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"code": -1, "msg": "账号不存在"})

        # 验证密码
        if user['password'] != password:
            return jsonify({"code": -1, "msg": "密码错误"})

        # 登录成功
        return jsonify({"code": 0, "msg": "登录成功"})

    except Exception as e:
        return jsonify({"code": -1, "msg": f"服务器错误：{str(e)}"})
    finally:
        if 'conn' in locals():
            conn.close()


# ================== 注册接口 ==================
@app.route('/api/register', methods=['OPTIONS', 'POST'])
def register():
    # 处理跨域预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 解析请求数据
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()  # 邮箱是可选的
    
    # 校验参数
    if not username or not password:
        return jsonify({"code": -1, "msg": "请输入账号和密码"})
    if len(username) < 3:
        return jsonify({"code": -1, "msg": "账号长度不能少于3位"})
    if len(password) < 6:
        return jsonify({"code": -1, "msg": "密码长度不能少于6位"})
    
    # 数据库操作
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查用户名是否已存在
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"code": -1, "msg": "账号已存在"})
        
        # 插入新用户
        sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, password, email))
        conn.commit()
        
        return jsonify({"code": 0, "msg": "注册成功"})
    
    except Exception as e:
        conn.rollback()
        return jsonify({"code": -1, "msg": f"注册失败：{str(e)}"})
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)