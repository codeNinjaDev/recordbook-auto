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

from database import *
from helpers import apology

# ENDPOINTS

def student_index(db):

    session["pending_invites"] = len(Invitation.query.filter_by(student_id=session["user_id"]).all())


    leadership_experiences = Leadership.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    service_experiences = Service.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    awards = Award.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    careers =  Career.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()

    email = Student.query.filter_by(id=session["user_id"]).first().username + ".docx"
    try:
        os.remove(email)
    except:
        pass
    return render_template("index.html", user="student", leadership=leadership_experiences, service=service_experiences, awards=awards, career=careers)


def student_info(request, db):
    curr_student = Student.query.filter_by(id=session["user_id"]).first()
    if request.method == "POST":

        if request.form.get("name"):
            curr_student.name = request.form.get("name")
        if request.form.get("county"):
            curr_student.county = request.form.get("county")
        if request.form.get("district"):
            curr_student.district = request.form.get("district")
        if request.form.get("category"):
            curr_student.category = request.form.get("category")
        if request.form.get("division"):
            curr_student.division = request.form.get("division")
        if request.form.get("club"):
            curr_student.club_name = request.form.get("club")
        db.session.commit()


    return render_template("info.html", user="student", name =xstr(curr_student.name), county =xstr(curr_student.county),
        district =xstr(curr_student.district), category=xstr(curr_student.category),
        division=xstr(curr_student.division), club=xstr(curr_student.club_name))

def student_activity(request, db, session):
    if request.method == "POST":
        form_type = request.form.get("type")

        if form_type == "leadership":

            year = request.form.get("year")
            activity = request.form.get("l-activity")
            role = request.form.get("l-roles")
            level = request.form.get("l-level")
            duties = request.form.get("duties")

            leadership = Leadership(user_id=session["user_id"], user_type="STUDENT", year=year, activity=activity,
                role=role, level=level, duties=duties)
            db.session.add(leadership)

        elif form_type == "service":
            year = request.form.get("year")
            activity = request.form.get("s-activity")
            role = request.form.get("s-roles")
            impact = request.form.get("impact")

            service = Service(user_id=session["user_id"], user_type="STUDENT", year=year, activity=activity,
                role=role, impact=impact)
            db.session.add(service)

        elif form_type == "award":

            year = request.form.get("year")
            recognition = request.form.get("a-recognition")
            level = request.form.get("a-levels")
            importance = request.form.get("importance")

            award = Award(user_id=session["user_id"], user_type="STUDENT", year=year, level=level,
                recognition=recognition, importance=importance)
            db.session.add(award)


        elif form_type == "career":

            year = request.form.get("year")
            activity = request.form.get("c-activity")
            importance = request.form.get("importance")
            career = Career(user_id=session["user_id"], user_type="STUDENT", year=year,
                activity=activity, importance=importance)
            db.session.add(career)
        else:
            return render_template("add_activity.html", user="student")

        db.session.commit()
        return redirect("/student")

    else:
        return render_template("add_activity.html", user="student")


def student_generate_book(db, session):
    curr_student = Student.query.filter_by(id=session["user_id"]).first()
    email = curr_student.username + ".docx"

    shutil.copyfile("report-form.docx", email)
    writer = RecordbookWriter(email)

    leadership_experiences = Leadership.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    service_experiences = Service.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    awards = Award.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    careers =  Career.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()

    writer.fill_info(name=curr_student.name, county=curr_student.county, district=curr_student.district,
        category=curr_student.category, division=curr_student.division)
    for entry in leadership_experiences:
        writer.append_leadership(entry.activity, entry.role, entry.level, year=entry.year, duties=entry.duties)

    for entry in service_experiences:
        writer.append_service(entry.role, entry.activity, year=entry.year, impact=entry.impact)

    for entry in awards:
        writer.append_award(entry.level, entry.recognition, year=entry.year, importance=entry.importance)

    for entry in careers:
        writer.append_career(entry.activity, year=entry.year, importance=entry.importance)

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
        return render_template("login.html", user="student")

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
            return render_template("register.html", user="student", error=True)

        student = Student(username=username, psswd_hash=password_hash)
        db.session.add(student)
        db.session.commit()
        session["pending_invite"] = 0
        return redirect('/student/login')
    else:
        """Register user"""
        return render_template("register.html", user="student", error=False)

def student_invites(request, db):

    if request.method == "POST":

        username = request.form.get("email")
        accept = request.form.get("type")
        # TODO possible bug with duplicate emails
        curr_invitation = Invitation.query.filter_by(email=username).first()


        if accept == "delete":
            db.session.delete(curr_invitation)
            db.session.commit()
            invitations = Invitation.query.filter_by(student_id=session["user_id"]).all()

            return render_template("user_invitations.html", invites=invitations)

        manager_id = Manager.query.filter_by(username=username).first().id

        curr_student = Student.query.filter_by(id=session["user_id"]).first()
        curr_student.club_name = curr_invitation.club_name
        db.session.delete(curr_invitation)
        curr_student.manager_id = manager_id
        db.session.commit()

        return redirect('/student/')
    else:
        invitations = Invitation.query.filter_by(student_id=session["user_id"]).all()
        return render_template("user_invitations.html", invites=invitations)
