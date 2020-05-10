import os
import shutil

import json
from docx import Document
from recordbook_writer import RecordbookDict, RecordbookWriter, LeadershipRole, ServiceRole, Level
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, flash, url_for, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from user import *
from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///record.db")


@app.route("/")
@app.route("/home")
@login_required
def index_user():
    return user_index(db)

@app.route("/info", methods=["GET", "POST"])
@login_required
def info_user():
    return user_info(request, db)


@app.route("/activity", methods=["GET", "POST"])
@login_required
def add_activity_user():
    return user_activity(request, db, session)


@app.route("/generatedocx")
@login_required
def generate_book_user():
    return user_generate_book(db, session)

@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Log user in"""
    return user_login(request, db, session)


@app.route("/logout")
def logout_user():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/reset", methods=["GET", "POST"])
@login_required
def reset_user():
    return user_reset(request, db, session)



@app.route("/register", methods=["GET", "POST"])
def register_user():
    return user_register(request, db)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
