from flask import Flask
from flask_login import LoginManager, UserMixin

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, email, password, name):
        self.id = id
        self.email = email
        self.password = password
        self.name = name

if __name__ == '__main__':
    app.run(debug=True)