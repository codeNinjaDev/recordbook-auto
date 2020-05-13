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

from helpers import apology
from database import Manager, Student, db

# USER DATA FUNCTIONS

# Gets user's data
def get_dict(db):
    file_path = Manager.query.filter_by(id=session["manager_id"]).first().file_path
    with open(file_path) as json_file:
        file = json.load(json_file)
        return file


# Gets user's data
def dump_dict(file, db):
    file_path = Manager.query.filter_by(id=session["manager_id"]).first().file_path
    with open(file_path, "w") as json_file:
        json.dump(file, json_file)
        return

# ENDPOINTS

def manager_index(db):
    data = get_dict(db)
    email = Manager.query.filter_by(id=session["manager_id"]).first().username + ".docx"
    try:
        os.remove(email)
    except:
        pass
    return render_template("manager.html", leadership=data["leadership"], service=data["service"], awards=data["awards"], career=data["career"])


def manager_info(request, db):
    file = get_dict(db)
    if request.method == "POST":

        if request.form.get("name"):
            file["personal_info"]["name"] = request.form.get("name")
        if request.form.get("county"):
            file["personal_info"]["county"] = request.form.get("county")
        if request.form.get("district"):
            file["personal_info"]["district"] = request.form.get("district")
        if request.form.get("club"):
            file["personal_info"]["club"] = request.form.get("club")
        dump_dict(file, db)

    return render_template("manager_info.html", name=file["personal_info"]["name"], county=file["personal_info"]["county"],
        district=file["personal_info"]["district"], club=file["personal_info"]["club"])

def manager_activity(request, db, session):

    users = [student.username for student in Student.query.filter_by(manager_id=session["manager_id"]).all()]
    print(users)

    if request.method == "POST":
        selected_user_emails = request.form.getlist("users")
        user_file_paths = []
        print(selected_user_emails)
        for email in selected_user_emails:
            user_file_paths.append(Student.query.filter_by(username=email).first().file_path)
            print(email)

        file_path = Manager.query.filter_by(id=session["manager_id"]).first().file_path

        form_type = request.form.get("type")

        if form_type == "leadership":

            year = request.form.get("year")
            activity = request.form.get("l-activity")
            role = request.form.get("l-roles")
            level = request.form.get("l-level")
            duties = request.form.get("duties")

            json_leadership(db, file_path, year=year, activity=activity, role=role, level=level, duties=duties)
            for path in user_file_paths:
                json_leadership(db, path, year=year, activity=activity, role=role, level=level, duties=duties)

            return redirect("/manager")

        elif form_type == "service":

            year = request.form.get("year")
            activity = request.form.get("s-activity")
            role = request.form.get("s-roles")
            impact = request.form.get("impact")

            json_service(db, file_path, year=year, activity=activity, role=role, impact=impact)

            for path in user_file_paths:
                json_service(db, path, year=year, activity=activity, role=role, impact=impact)

            return redirect("/manager")

        elif form_type == "award":

            year = request.form.get("year")
            recognition = request.form.get("a-recognition")
            level = request.form.get("a-levels")
            importance = request.form.get("importance")


            json_awards(db, file_path, year=year, recognition=recognition, level=level, importance=importance)
            for path in user_file_paths:
                json_awards(db, path, year=year, recognition=recognition, level=level, importance=importance)
            return redirect("/manager")

        elif form_type == "career":
            year = request.form.get("year")
            activity = request.form.get("c-activity")
            importance = request.form.get("importance")

            json_career(db, file_path, year=year, activity=activity, importance=importance)
            for path in user_file_paths:
                json_career(db, path, year=year, activity=activity, importance=importance)

            return redirect("/manager")
        else:
            return render_template("manager_add_activity.html", users=users)
    else:
        return render_template("manager_add_activity.html", users=users)

def manager_generate_book(db, session):
    data = get_dict(db)
    email = Manager.query.filter_by(id=session["manager_id"]).first().username + ".docx"

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

def manager_login(request, db, session):
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
        manager = Manager.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not manager or not check_password_hash(manager.psswd_hash, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["manager_id"] = manager.id

        # Redirect user to home page
        return redirect("/manager")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("manager_login.html")

def manager_reset(request, db, session):
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        manager = Manager.query.filter_by(id=session["manager_id"]).first()

        password_hash = manager.psswd_hash
        if not check_password_hash(password_hash, request.form.get("oldPassword")):
            return render_template("reset.html", error=True)

        manager.psswd_hash =generate_password_hash(request.form.get("newPassword"))
        db.session.commit()

        flash("Reset password")
        return redirect("/manager")

    else:
        return render_template("manager_reset.html", error=False)

def manager_register(request, db):
    if request.method == "POST":

        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))
        # Query database for username
        managers = Manager.query.filter_by(username=username).all()

        if managers:
            return render_template("manager_register.html", error=True)

        dir_path = "./data/manager/" + str(username) + "/"
        file_path = dir_path + str(username) + ".json"
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        book_dict = RecordbookDict().create_recordbook_dict()

        with open(file_path, "w") as fp:
            json.dump(book_dict, fp)

        manager = Manager(username=username, psswd_hash=password_hash, file_path=file_path)
        db.session.add(manager)
        db.session.commit()
        return redirect('/manager/login')
    else:
        """Register manager"""
        return render_template("manager_register.html", error=False)

def manager_invite(request, db, session):

    username = Manager.query.filter_by(id=session["manager_id"]).first().username


    if request.method == "POST":
        user_email = request.form.get("email")
        data = get_dict(db)

        if data["personal_info"]["club"]:
            club_name = data["personal_info"]["club"]
        else:
            club_name = request.form.get("name")

        try:
            path = Student.query.filter_by(username=user_email).first().file_path
            with open(path) as json_file:
                file = json.load(json_file)
                if "invitations" not in file.keys():
                    file["invitations"] = dict()
                file["invitations"][username] = club_name
                with open(path, "w") as dump_file:
                    json.dump(file, dump_file)
                return redirect("/manager")
        except:
            return render_template("manager_invite.html")


    return render_template("manager_invite.html")

def json_leadership(db, path, year="", role="", level="", activity="", duties=""):
    with open(path) as json_file:
        file = json.load(json_file)
        file["leadership"].append({
                "year": year,
                "activity": activity,
                "role": role,
                "level": level,
                "duties": duties
            })
        with open(path, "w") as fp:
            json.dump(file, fp)
def json_service(db, path, year="", role="", activity="", impact=""):
    with open(path) as json_file:
        file = json.load(json_file)
        file["service"].append({
                "year": year,
                "role": role,
                "activity": activity,
                "impact": impact
            })
        with open(path, "w") as fp:
            json.dump(file, fp)
def json_awards(db, path, year="", level="", recognition="", importance=""):
    with open(path) as json_file:
        file = json.load(json_file)
        file["awards"].append({
                "year": year,
                "level": level,
                "recognition": recognition,
                "importance": importance
            })
        with open(path, "w") as fp:
            json.dump(file, fp)

def json_career(db, path, year="", activity="", importance=""):
    with open(path) as json_file:
        file = json.load(json_file)
        file["career"].append({
                "year": year,
                "activity": activity,
                "importance": importance
            })
        with open(path, "w") as fp:
            json.dump(file, fp)