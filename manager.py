import os
import shutil

import json
from docx import Document
from recordbook_writer import xstr, RecordbookDict, RecordbookWriter, LeadershipRole, ServiceRole, Level
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, flash, url_for, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology
from database import *

# ENDPOINTS

def manager_index(db):


    leadership_experiences = Leadership.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    service_experiences = Service.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    awards = Award.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    careers =  Career.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()

    email = Student.query.filter_by(id=session["manager_id"]).first().username + ".docx"
    try:
        os.remove(email)
    except:
        pass
    return render_template("index.html", user="manager", leadership=leadership_experiences, service=service_experiences, awards=awards, career=careers)


def manager_info(request, db):
    curr_manager = Student.query.filter_by(id=session["manager_id"]).first()
    if request.method == "POST":

        if request.form.get("name"):
            curr_manager.name = request.form.get("name")
        if request.form.get("county"):
            curr_manager.county = request.form.get("county")
        if request.form.get("district"):
            curr_manager.district = request.form.get("district")
        if request.form.get("club"):
            curr_manager.club_name = request.form.get("club")
        db.session.commit()


    return render_template("info.html", user="manager", name =xstr(curr_manager.name), county =xstr(curr_manager.county),
        district =xstr(curr_manager.district), club=xstr(curr_manager.club_name))

def manager_activity(request, db, session):
    students = [student.username for student in Student.query.filter_by(manager_id=session["manager_id"]).all()]

    selected_users = []

    if request.method == "POST":
        selected_user_emails = request.form.getlist("users")

        for email in selected_user_emails:

            selected_users.append(Student.query.filter_by(username=email).first())

        form_type = request.form.get("type")

        if form_type == "leadership":

            year = request.form.get("year")
            activity = request.form.get("l-activity")
            role = request.form.get("l-roles")
            level = request.form.get("l-level")
            duties = request.form.get("duties")

            input_leadership(db, session["manager_id"], user_type="MANAGER", year=year, activity=activity, role=role, level=level, duties=duties)
            for user in selected_users:
                input_leadership(db, user.id, user_type="STUDENT", year=year, activity=activity, role=role, level=level, duties=duties)


        elif form_type == "service":

            year = request.form.get("year")
            activity = request.form.get("s-activity")
            role = request.form.get("s-roles")
            impact = request.form.get("impact")

            input_service(db, session["manager_id"], user_type="MANAGER", year=year, activity=activity, role=role, impact=impact)
            for user in selected_users:
                input_service(db, user.id, user_type="STUDENT", year=year, activity=activity, role=role, impact=impact)

        elif form_type == "award":

            year = request.form.get("year")
            recognition = request.form.get("a-recognition")
            level = request.form.get("a-levels")
            importance = request.form.get("importance")


            input_awards(db, session["manager_id"], user_type="MANAGER", year=year, recognition=recognition, level=level, importance=importance)
            for user in selected_users:
                input_awards(db, user.id, user_type="STUDENT", year=year, recognition=recognition, level=level, importance=importance)


        elif form_type == "career":
            year = request.form.get("year")
            activity = request.form.get("c-activity")
            importance = request.form.get("importance")

            input_career(db, session["manager_id"], user_type="MANAGER", year=year, activity=activity, importance=importance)
            for user in selected_users:
                input_award(db, user.id, user_type="STUDENT", year=year, activity=activity, importance=importance)

        else:
            return render_template("add_activity.html", user="manager", students=students)

        return redirect("/manager")
    else:
        return render_template("add_activity.html", user="manager", students=students)

def manager_generate_book(db, session):
    curr_manager = Student.query.filter_by(id=session["manager_id"]).first()
    email = curr_manager.username + ".docx"

    shutil.copyfile("report-form.docx", email)
    writer = RecordbookWriter(email)

    leadership_experiences = Leadership.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    service_experiences = Service.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    awards = Award.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    careers =  Career.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()

    writer.fill_info(name=curr_manager.name, county=curr_manager.county, district=curr_manager.district,
        category=curr_manager.category, division=curr_manager.division)
    for entry in leadership_experiences:
        writer.append_leadership(entry.activity, entry.role, entry.level, year=entry.year, duties=entry.duties)

    for entry in service_experiences:
        writer.append_service(entry.role, entry.activity, year=entry.year, impact=entry.impact)

    for entry in awards:
        writer.append_award(entry.level, entry.recognition, year=entry.year, importance=entry.importance)

    for entry in careers:
        writer.append_career(entry.activity, year=entry.year, importance=entry.importance)

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
        return render_template("login.html", user="manager")

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
            return render_template("register.html", user="manager", error=True)

        manager = Manager(username=username, psswd_hash=password_hash)
        db.session.add(manager)
        db.session.commit()
        return redirect('/manager/login')
    else:
        """Register manager"""
        return render_template("register.html", user="manager", error=False)

def manager_invite(request, db, session):

    manager = Manager.query.filter_by(id=session["manager_id"]).first()

    if request.method == "POST":
        user = Student.query.filter_by(username=request.form.get("email")).first()
        if not user:
            return render_template("manager_invite.html")

        if manager.club_name:
            club_name = manager.club_name
        else:
            club_name = request.form.get("name")

        try:
            invite = Invitation(student_id=user.id, manager_id=manager.id, club_name=club_name, email=manager.username)
            db.session.add(invite)
            db.session.commit()
            return redirect("/manager")
        except:
            return render_template("manager_invite.html")


    return render_template("manager_invite.html")

def input_leadership(db, user, user_type="STUDENT", year="", role="", level="", activity="", duties=""):

    leadership = Leadership(user_id=user, user_type=user_type, year=year, activity=activity,
        role=role, level=level, duties=duties)
    db.session.add(leadership)
    db.session.commit()

def input_service(db, user, user_type="STUDENT", year="", role="", activity="", impact=""):
    service = Service(user_id=user, user_type=user_type, year=year, activity=activity,
                role=role, impact=impact)
    db.session.add(service)
    db.session.commit()

def input_awards(db, user, user_type="STUDENT", year="", level="", recognition="", importance=""):
    award = Award(user_id=user, user_type=user_type, year=year, level=level,
                recognition
                =recognition, importance=importance)
    db.session.add(award)
    db.session.commit()

def input_career(db, user, user_type="STUDENT", year="", activity="", importance=""):
    career = Career(user_id=user, user_type=user_type, year=year,
        activity=activity, importance=importance)
    db.session.add(career)
    db.session.commit()
