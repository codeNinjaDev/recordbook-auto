#!/usr/bin/python3
import os
import shutil

import json
from docx import Document
from recordbook_writer import RecordbookWriter, LeadershipRole, ServiceRole, Level
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, flash, url_for, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from database import *
from student import *
from manager import *
from helpers import apology, student_login_required, manager_login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.secret_key = b'_5#y2L"G3R8z\n\xec]'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DATABASE_URL']
app.config['SESSION_COOKIE_SECURE'] = True

db.init_app(app)
csrf = CSRFProtect(app)


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

with app.app_context():
    try:
        db.create_all()
        if not "csrf_token" in session.keys():
            session["csrf_token"] = ""
    except:
        pass

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/student/", methods=["GET", "POST"])
@student_login_required
def index_student():
    return student_index(db, request)

@app.route("/student/info", methods=["GET", "POST"])
@student_login_required
def info_student():
    return student_info(request, db)


@app.route("/student/activity", methods=["GET", "POST"])
@student_login_required
def add_activity_student():
    return student_activity(request, db, session)


@app.route("/student/generatedocx")
@student_login_required
def generate_book_student():
    return student_generate_book(db, session)

@app.route("/student/login", methods=["GET", "POST"])
def login_student():
    """Log student in"""
    return student_login(request, db, session)

@app.route("/student/delete_account", methods=["GET", "POST"])
@student_login_required
def delete_student():
    return student_delete(db, request)

@app.route("/student/logout")
def logout_student():
    """Log student out"""
    # Forget any student_id
    session.clear()

    # Redirect student to login form
    return redirect("/")

@app.route("/student/reset", methods=["GET", "POST"])
@student_login_required
def reset_student():
    return student_reset(request, db, session)

@app.route("/student/register", methods=["GET", "POST"])
def register_student():
    return student_register(request, db)

@app.route("/student/invites", methods=["GET", "POST"])
@student_login_required
def invites_student():
    return student_invites(request, db)

@app.route("/student/generatejournal")
@student_login_required
def generate_journal_student():
    return student_generate_journal(db, session)

# MANAGER endpoints

@app.route("/manager/", methods=["GET", "POST"])
@manager_login_required
def index_manager():
    return manager_index(db, request)

@app.route("/manager/delete_account", methods=["GET", "POST"])
@manager_login_required
def delete_manager():
    return manager_delete(db, request)

@app.route("/manager/info", methods=["GET", "POST"])
@manager_login_required
def info_manager():
    return manager_info(request, db)

@app.route("/manager/activity", methods=["GET", "POST"])
@manager_login_required
def add_activity_manager():
    return manager_activity(request, db, session)

@app.route("/manager/invite", methods=["GET", "POST"])
@manager_login_required
def manage_invites():
    return manager_invite(request, db, session)


@app.route("/manager/generatedocx")
@manager_login_required
def generate_book_manager():
    return manager_generate_book(db, session)

@app.route("/manager/generatejournal")
@manager_login_required
def generate_journal_manager():
    return manager_generate_journal(db, session)

@app.route("/manager/login", methods=["GET", "POST"])
def login_manager():
    """Log manager in"""
    return manager_login(request, db, session)

@app.route("/manager/logout")
def logout_manager():
    """Log manager out"""
    # Forget any manager_id
    session.clear()

    # Redirect manager to login form
    return redirect("/")

@app.route("/manager/reset", methods=["GET", "POST"])
@manager_login_required
def reset_manager():
    return manager_reset(request, db, session)

@app.route("/manager/register", methods=["GET", "POST"])
def register_manager():
    return manager_register(request, db)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    print(e)
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

