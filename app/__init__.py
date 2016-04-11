from flask import Flask
from flask.ext.cors import CORS
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask.ext.httpauth import HTTPBasicAuth
from flask_mail import Mail


app=Flask(__name__)
manager=Manager(app)
CORS(app)
mail=Mail(app)
app.secret_key="reality is broken"
app.config.from_object("config")
db=SQLAlchemy(app)
migrate=Migrate(app,db)
auth=HTTPBasicAuth()

from app import models,views
