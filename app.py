
from flask import Flask, render_template, request, redirect, url_for, send_file, session
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

project_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_dir, 'user_data.db')

def init_db():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT
            )
        ''')
        conn.commit()

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        name = request.form['name']
        phone = request.form['phone']
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (name, phone) VALUES (?, ?)", (name, phone))
            conn.commit()
        return render_template('submit.html')
    except Exception as e:
        return f"오류 발생: {e}"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'a192837456':
            session['logged_in'] = True
            return redirect(url_for('download_excel'))
        else:
            return "로그인 실패"
    return render_template('admin_login.html')

@app.route('/admin/download')
def download_excel():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM users", conn)
        file_path = os.path.join(project_dir, "user_data.xlsx")
        df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

