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
    'host': "localhost",
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
            return render_template('registration_success.html'), 201
        
        except mysql.connector.Error as e:
            return render_template('registration.html', errors=[str(e)]), 400

    elif request.method == 'GET':
        # GET 请求，显示注册表单
        return render_template('registration.html'), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)