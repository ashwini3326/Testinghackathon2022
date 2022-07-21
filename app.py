from flask import Flask, request, render_template, flash, redirect, url_for,session, logging, send_file, jsonify, Response, render_template_string
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateTimeField, BooleanField, IntegerField, DecimalField, HiddenField, SelectField, RadioField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_mail import Mail, Message
from functools import wraps
from werkzeug.utils import secure_filename

from datetime import timedelta, datetime
import operator
import functools
import math, random
import csv

import json
import base64
from wtforms_components import TimeField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, NumberRange
from flask_session import Session
from flask_cors import CORS, cross_origin



app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_PASSWORD'] = 'root123$'
app.config['MYSQL_DB'] = 'infringementsuite'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.config['MAIL_SERVER'] = 'email-smtp.us-east-2.amazonaws.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'AKIAZCKYMJZLSNHWIW7E'
app.config['MAIL_PASSWORD'] = 'BEeIIBdE6NcbKBo/8yyvqmJz3lHz7L+lC56TxzG5+x1S'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['SESSION_COOKIE_SAMESITE'] = "None"

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
mail = Mail(app)

sess = Session()
sess.init_app(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key= 'backtrack'

mysql = MySQL(app)
sender = 'sridharpothamsetti@gmail.com'

YOUR_DOMAIN = 'http://localhost:5001'
@app.before_request
def make_session_permanent():
	session.permanent = True

@app.route('/')
def index():
	return render_template('index.html')

# @app.errorhandler(404)
# def not_found(e):
# 	return render_template("404.html")
#
# @app.errorhandler(500)
# def internal_error(error):
# 	return render_template("500.html")

if __name__ == "__main__":
	app.run(host = "0.0.0.0",debug=False)