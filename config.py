import os
from flask import Flask
from flaskext.mysql import MySQL

# project root directory
DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
SECRET_KEY = 'This !s my secre+ key!'

MYSQL_DATABASE_HOST = "localhost"
MYSQL_DATABASE_PORT = 3306
MYSQL_DATABASE_USER = "instaclone"
MYSQL_DATABASE_PASSWORD = "instaclone"
MYSQL_DATABASE_DB = "instaclone"

# create our application
app = Flask(__name__)
app.config.from_object(__name__)

db = MySQL()
db.init_app(app)
