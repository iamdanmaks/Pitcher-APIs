from flask import Flask
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_optimize import FlaskOptimize
from config import Config
from flask_login import LoginManager


app = Flask(__name__)
flask_optimize = FlaskOptimize()
Compress(app)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes, models, functions, update
