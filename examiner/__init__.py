from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)

# TODO what does this secret key do? can i hide it?
app.config['SECRET_KEY'] = '2ebec24232814cf6844dfd6edd068fc3'
# to generate secrets in python
# import secretsw
# secrets.token_hex(16)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rain_students.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# this is used to redirect users to login page whenever they try
# to access a route that requires login authorization
login_manager.login_view = 'exam_login'



from examiner import routes