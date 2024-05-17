from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = "hjasgdikuhqhjkgavsasudmnxbzcjyatwakjhsh"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/student_management?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["CN_PAGE_SIZE"] = 9


db = SQLAlchemy(app= app)
login = LoginManager(app)

cloudinary.config(
    cloud_name = 'ddwmpk2nq',
    api_key = '711575846868493',
    api_secret = '_MmgQvCsPZ2xzGHnZhdEJN8i7Pk'
)