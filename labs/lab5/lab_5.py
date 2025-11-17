from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('flask_secret', 'secret-key')
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, email, password, name):
        self.id = id
        self.email = email
        self.password = password
        self.name = name

def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        database='lab5_rpp_db',
        user='postgres',
        password=os.getenv('5lb_db_password', 'password')
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(100) NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3])
    return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    email_value = ""

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        email_value = email

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if not user_data:
            error = "Пользователь не найден"
        elif not check_password_hash(user_data[2], password):
            error = "Неверный пароль"
        else:
            user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            login_user(user)
            return redirect('/')

    return render_template('login.html', error=error, email=email_value)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    name_value = ""
    email_value = ""

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        name_value = name
        email_value = email

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        if cur.fetchone():
            error = "Пользователь с таким email уже существует"
        else:
            cur.execute(
                'INSERT INTO users (email, password, name) VALUES (%s, %s, %s)',
                (email, generate_password_hash(password), name)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect('/login')

        cur.close()
        conn.close()

    return render_template('signup.html', error=error, name=name_value, email=email_value)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)