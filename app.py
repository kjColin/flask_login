# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template
import re
import hashlib
import mysql.connector
from flask import redirect, url_for

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'user': "root",
    'password': "86991975",
    'host': "45.63.1.224",
    'port': 3306,
    'database': "mydatabase"
}

# 获取数据库连接
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# 初始化数据库结构
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("CREATE DATABASE IF NOT EXISTS mydatabase")
    c.execute("USE mydatabase")
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INT AUTO_INCREMENT PRIMARY KEY,
                  name VARCHAR(255) NOT NULL,
                  email VARCHAR(255) UNIQUE NOT NULL,
                  password VARCHAR(255) NOT NULL);''')
    conn.commit()
    conn.close()

# 调用init_db函数确保数据库结构存在
init_db()

# 处理用户注册
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        errors = []
        if not name or not email or not password or not confirm_password:
            errors.append("所有字段都是必填项。")
        if password != confirm_password:
            errors.append("密码和确认密码不一致。")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("请输入有效的电子邮件地址。")

        if errors:
            return render_template('registration.html', errors=errors), 400

        # 加密密码
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # 存储用户信息
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                      (name, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login_user')), 201
        
        except mysql.connector.Error as e:
            return render_template('registration.html', errors=[str(e)]), 400

    elif request.method == 'GET':
        # GET 请求，显示注册表单
        return render_template('registration.html'), 200
# 添加登录功能
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        errors = []
        if not email or not password:
            errors.append("邮箱和密码都是必填项。")

        if errors:
            return render_template('login.html', errors=errors), 400

        # 验证用户信息
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = c.fetchone()
            conn.close()

            if user:
                # 验证密码
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if hashed_password == user[3]:  # 假设密码在数据库中的索引是3
                    # 登录成功，重定向到登录成功页面
                    return redirect(url_for('login_success'))
                else:
                    errors.append("密码不正确。")
            else:
                errors.append("用户不存在。")

            return render_template('login.html', errors=errors), 400

        except mysql.connector.Error as e:
            return render_template('login.html', errors=[str(e)]), 400

    elif request.method == 'GET':
        # GET 请求，显示登录表单
        return render_template('login.html'), 200
@app.route('/login/success')
def login_success():
    # 可以在这里添加登录成功后的逻辑，如设置 session 或 cookie
    return render_template('login_success.html'), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
