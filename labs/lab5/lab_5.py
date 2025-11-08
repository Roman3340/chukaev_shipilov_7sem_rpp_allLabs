from flask import Flask
from flask_login import LoginManager, UserMixin
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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
        database='lab5_db',
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
            password VARCHAR(100) NOT NULL,
            name VARCHAR(100) NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)