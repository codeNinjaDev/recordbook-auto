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
def index():
    data = get_dict()
    return render_template("index.html", leadership=data["leadership"])

@app.route("/activity", methods=["GET", "POST"])
@login_required
def add_activity():

    if request.method == "POST":
        form_type = request.form.get("type")

        if form_type == "leadership":
            year = request.form.get("year")
            activity = request.form.get("l-activity")
            role = request.form.get("l-roles")
            level = request.form.get("l-level")
            duties = request.form.get("duties")
            file_path = str(db.execute("SELECT file_path FROM users WHERE id = :id",
                          id=session["user_id"])[0]["file_path"])

            file_path = str(db.execute("SELECT file_path FROM users WHERE id = :id",
                                  id=session["user_id"])[0]["file_path"])

            with open(file_path) as json_file:
                file = json.load(json_file)
                file["leadership"].append({
                        "year": year,
                        "activity": activity,
                        "role": role,
                        "level": level,
                        "duties": duties
                    })
                with open(file_path, "w") as fp:
                    json.dump(file, fp)
            return redirect("/")
        elif form_type == "service":
            pass
        else:
            return render_template("add_activity.html")
    else:
        return render_template("add_activity.html")


@app.route("/history")
@login_required
def history():
    return render_template("history.html")

@app.route("/generatedocx")
@login_required
def generate_book():
    data = get_dict()

    email = str(db.execute("SELECT username FROM users WHERE id = :id",
                      id=session["user_id"])[0]["username"]) + ".docx"

    shutil.copyfile("report-form.docx", email)
    writer = RecordbookWriter(email)

    for entry in data["leadership"]:
        writer.append_leadership(entry["activity"], entry["role"], entry["level"], year=entry["year"], duties=entry["duties"])

    return send_file(email, as_attachment=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/reset", methods=["GET", "POST"])
@login_required
def reset():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        password_hash = next(iter(db.execute("SELECT hash FROM users WHERE id = :user_id",
                          user_id=session["user_id"])[0].values()))
        if not check_password_hash(password_hash, request.form.get("oldPassword")):
            return render_template("reset.html", error=True)

        db.execute("UPDATE users SET hash = :pass_hash WHERE id = :user_id",
            pass_hash=generate_password_hash(request.form.get("newPassword")), user_id=session["user_id"])
        flash("Reset password")
        return redirect("/")

    else:
        return render_template("reset.html", error=False)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)
        print(rows)
        if len(rows) != 0:
            return render_template("register.html", error=True)

        dir_path = "./data/" + str(username) + "/"
        file_path = dir_path + str(username) + ".json"
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        book_dict = RecordbookDict().create_recordbook_dict()

        with open(file_path, "w") as fp:
            json.dump(book_dict, fp)

        db.execute("INSERT INTO users (username, hash, file_path) VALUES (:username, :password_hash, :path)", username=username, password_hash=password_hash, path=file_path)
        return redirect('/login')
    else:
        """Register user"""
        return render_template("register.html", error=False)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
def get_dict():
    file_path = str(db.execute("SELECT file_path FROM users WHERE id = :id",
                          id=session["user_id"])[0]["file_path"])
    with open(file_path) as json_file:
        file = json.load(json_file)
        return file
