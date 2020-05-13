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

from database import Student, Manager
from helpers import apology

# USER DATA FUNCTIONS

# Gets user's data
def get_dict(db):
    file_path = Student.query.filter_by(id=session["user_id"]).first().file_path
    with open(file_path) as json_file:
        file = json.load(json_file)
        return file

# Gets user's data
def dump_dict(file, db):
    file_path = Student.query.filter_by(id=session["user_id"]).first().file_path

    with open(file_path, "w") as json_file:
        json.dump(file, json_file)
        return

# ENDPOINTS

def student_index(db):
    data = get_dict(db)
    email = Student.query.filter_by(id=session["user_id"]).first().username + ".docx"
    try:
        os.remove(email)
    except:
        pass
    return render_template("user.html", leadership=data["leadership"], service=data["service"], awards=data["awards"], career=data["career"])


def student_info(request, db):
    file = get_dict(db)
    if request.method == "POST":

        if request.form.get("name"):
            file["personal_info"]["name"] = request.form.get("name")
        if request.form.get("county"):
            file["personal_info"]["county"] = request.form.get("county")
        if request.form.get("district"):
            file["personal_info"]["district"] = request.form.get("district")
        if request.form.get("category"):
            file["personal_info"]["category"] = request.form.get("category")
        if request.form.get("division"):
            file["personal_info"]["division"] = request.form.get("division")
        if request.form.get("club"):
            file["personal_info"]["club"] = request.form.get("club")
        dump_dict(file, db)

    return render_template("user_info.html", name=file["personal_info"]["name"], county=file["personal_info"]["county"],
        district=file["personal_info"]["district"], category=file["personal_info"]["category"],
        division=file["personal_info"]["division"], club=file["personal_info"]["club"])

def student_activity(request, db, session):
    if request.method == "POST":
        file_path = Student.query.filter_by(id=session["user_id"]).first().file_path
        form_type = request.form.get("type")

        if form_type == "leadership":

            year = request.form.get("year")
            activity = request.form.get("l-activity")
            role = request.form.get("l-roles")
            level = request.form.get("l-level")
            duties = request.form.get("duties")

            with open(file_path) as json_file:
                file = json.load(json_file)
                file["leadership"].append({
                        "year": year,
                        "activity": activity,
                        "role": role,
                        "level": level,
                        "duties": duties
                    })
                dump_dict(file, db)

            return redirect("/student")

        elif form_type == "service":

            year = request.form.get("year")
            activity = request.form.get("s-activity")
            role = request.form.get("s-roles")
            impact = request.form.get("impact")

            with open(file_path) as json_file:
                file = json.load(json_file)
                file["service"].append({
                        "year": year,
                        "role": role,
                        "activity": activity,
                        "impact": impact
                    })
                dump_dict(file, db)
            return redirect("/student")

        elif form_type == "award":

            year = request.form.get("year")
            recognition = request.form.get("a-recognition")
            level = request.form.get("a-levels")
            importance = request.form.get("importance")


            with open(file_path) as json_file:
                file = json.load(json_file)
                file["awards"].append({
                        "year": year,
                        "level": level,
                        "recognition": recognition,
                        "importance": importance
                    })
                dump_dict(file, db)

            return redirect("/student")
        elif form_type == "career":
            year = request.form.get("year")
            activity = request.form.get("c-activity")
            importance = request.form.get("importance")

            with open(file_path) as json_file:
                file = json.load(json_file)
                file["career"].append({
                        "year": year,
                        "activity": activity,
                        "importance": importance
                    })
                dump_dict(file, db)
            return redirect("/student")
        else:
            return render_template("add_activity.html", user="student")
    else:
        return render_template("add_activity.html", user="student")


def student_generate_book(db, session):
    data = get_dict(db)
    email = Student.query.filter_by(id=session["user_id"]).first().username + ".docx"

    shutil.copyfile("report-form.docx", email)
    writer = RecordbookWriter(email)

    writer.fill_info(name=data["personal_info"]["name"], county=data["personal_info"]["county"], district=data["personal_info"]["district"],
        category=data["personal_info"]["category"], division=data["personal_info"]["division"])
    for entry in data["leadership"]:
        writer.append_leadership(entry["activity"], entry["role"], entry["level"], year=entry["year"], duties=entry["duties"])

    for entry in data["service"]:
        writer.append_service(entry["role"], entry["activity"], year=entry["year"], impact=entry["impact"])

    for entry in data["awards"]:
        writer.append_award(entry["level"], entry["recognition"], year=entry["year"], importance=entry["importance"])

    for entry in data["career"]:
        writer.append_career(entry["activity"], year=entry["year"], importance=entry["importance"])

    return send_file(email, as_attachment=True)

def student_login(request, db, session):
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
        student = Student.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not student or not check_password_hash(student.psswd_hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = student.id

        # Redirect user to home page
        return redirect("/student")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("user_login.html")

def student_reset(request, db, session):
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        curr_student = Student.query.filter_by(id=session["user_id"]).first()
        if not check_password_hash(curr_student.psswd_hash, request.form.get("oldPassword")):
            return render_template("reset.html", error=True)

        curr_student.psswd_hash = generate_password_hash(request.form.get("newPassword"))
        db.session.commit()
        flash("Reset password")
        return redirect("/student")

    else:
        return render_template("user_reset.html", error=False)

def student_register(request, db):
    if request.method == "POST":

        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))
        # Query database for username
        students = Student.query.filter_by(username=username).all()

        if students:
            return render_template("user_register.html", error=True)

        dir_path = "./data/" + str(username) + "/"
        file_path = dir_path + str(username) + ".json"
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        book_dict = RecordbookDict().create_recordbook_dict()

        with open(file_path, "w") as fp:
            json.dump(book_dict, fp)
        student = Student(username=username, psswd_hash=password_hash, file_path=file_path)
        db.session.add(student)
        db.session.commit()

        return redirect('/student/login')
    else:
        """Register user"""
        return render_template("user_register.html", error=False)

def student_invites(request, db):
    file = get_dict(db)
    if "invitations" not in file.keys():
        file["invitations"] = dict()
    if request.method == "POST":

        username = request.form.get("email")
        accept = request.form.get("type")

        if accept == "delete":
            file["invitations"].pop(username)
            dump_dict(file, db)
            return render_template("user_invitations.html", invites=file["invitations"])

        manager_id = Manager.query.filter_by(username=username).first().id

        file["personal_info"]["club"] = file["invitations"][username]
        file["invitations"].pop(username)
        dump_dict(file, db)
        student = Student.query.filter_by(id=session["user_id"]).first()
        student.manager_id = manager_id
        print(student.id)
        db.session.commit()

        return redirect('/student/')
    else:
        return render_template("user_invitations.html", invites=file["invitations"])
