from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os
from secrets import token_hex

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = token_hex()
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
