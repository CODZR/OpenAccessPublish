from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login.login_manager import LoginManager
from flask_mail import Mail
from config import Config
from flask_script import Manager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.session_protection = 'strong'
lm.login_view = '/login'
mail = Mail(app)
mail.init_app(app)
manager = Manager(app)
from views import *

if __name__ == '__main__':
    remove_captcha()
    remove_img()
    db.drop_all()
    db.create_all()
    print(123)
    # app.run(debug=True, port=5000)
    app.run(threaded=True,host='0.0.0.0', port=8080)
