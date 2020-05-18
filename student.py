import os
import shutil

import json

from flask import Flask, flash, jsonify, redirect, render_template, request, session, flash, url_for, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from docx import Document
from recordbook_writer import xstr, RecordbookWriter, JournalWriter

from database import *
from helpers import apology
from auth_forms import RegisterForm, LoginForm, login
from app_forms import LeadershipForm, ServiceForm, CareerForm, AwardForm, ProjectForm
# ENDPOINTS

def student_index(db):

    session["pending_invites"] = len(Invitation.query.filter_by(student_id=session["user_id"]).all())


    leadership_experiences = Leadership.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    service_experiences = Service.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    awards = Award.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    careers =  Career.query.filter_by(user_id=session["user_id"], user_type="STUDENT").all()
    projects =  Project.query.filter_by(user_id=session["user_id"], user_type="STUDENT").order_by(Project.project_name, Project.year.desc()).all()

    email = Student.query.filter_by(id=session["user_id"]).first().username + ".docx"
    journal = Student.query.filter_by(id=session["user_id"]).first().username + "journal.docx"

    try:
        os.remove(email)
        os.remove(journal)
    except:
        pass
    return render_template("index.html", user="student", projects=projects, leadership=leadership_experiences, service=service_experiences, awards=awards, career=careers)


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

    leadership_form = LeadershipForm()
    service_form = ServiceForm()
    career_form = CareerForm()
    award_form = AwardForm()
    project_form = ProjectForm()
    if leadership_form.lead_submit.data and leadership_form.validate_on_submit():
        leadership = Leadership(user_id=session["user_id"], user_type="STUDENT", year=leadership_form.year.data, activity=leadership_form.activity.data,
            role=leadership_form.role.data, level=leadership_form.level.data, duties=leadership_form.importance.data)
        db.session.add(leadership)
    elif service_form.service_submit.data and service_form.validate_on_submit():
        service = Service(user_id=session["user_id"], user_type="STUDENT", year=service_form.year.data, activity=service_form.activity.data,
            role=service_form.role.data, impact=service_form.importance.data)
        db.session.add(service)
    elif award_form.award_submit.data and award_form.validate_on_submit():
        award = Award(user_id=session["user_id"], user_type="STUDENT", year=award_form.year.data, level=award_form.level.data,
            recognition=award_form.recognition.data, importance=award_form.importance.data)
        db.session.add(award)
    elif career_form.career_submit.data and career_form.validate_on_submit():
        career = Career(user_id=session["user_id"], user_type="STUDENT", year=career_form.year.data,
            activity=career_form.activity.data, importance=career_form.importance.data)
        db.session.add(career)
    elif project_form.project_submit.data and project_form.validate_on_submit():
        project = Project(user_id=session["user_id"], user_type="STUDENT", project_name=project_form.project_name.data, year=project_form.year.data, hours=project_form.hours.data, activity=project_form.activity.data, importance=project_form.importance.data)
        db.session.add(project)
    else:
        return render_template("add_activity.html", leadership_form=leadership_form, service_form=service_form,
            award_form=award_form, career_form=career_form, project_form=project_form, user="student")

    db.session.commit()
    return redirect("/student")

def student_generate_journal(db, session):
    curr_student = Student.query.filter_by(id=session["user_id"]).first()
    journal_name = curr_student.username + ".journal.docx"
    journal = Document()
    journal.save(journal_name)

    writer = JournalWriter(journal_name)
    project_objects = Project.query.filter_by(user_id=session["user_id"], user_type="STUDENT").with_entities(Project.project_name).distinct()

    for project in project_objects:
        writer.create_project_table(project.project_name, Project.query.filter_by(user_id=session["user_id"], user_type="STUDENT", project_name=project.project_name).all())
    return send_file(journal_name, as_attachment=True)
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

    login_form = LoginForm()
    # User reached route via POST (as by submitting a form via POST)
    if login_form.validate_on_submit():
        # Ensure username exists and password is correct
        if login(db, login_form, session, user_type="student"):
            return redirect("/student")
        return apology("invalid username and/or password", 403)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", login_form=login_form, user="student")

def student_reset(request, db, session):
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        curr_student = Student.query.filter_by(id=session["user_id"]).first()
        if not check_password_hash(curr_student.psswd_hash, request.form.get("oldPassword")):
            return render_template("reset.html", user="student", error=True)

        curr_student.psswd_hash = generate_password_hash(request.form.get("newPassword"))
        db.session.commit()
        flash("Reset password")
        return redirect("/student")

    else:
        return render_template("reset.html", user="student",error=False)

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
    session["pending_invites"] = len(Invitation.query.filter_by(student_id=session["user_id"]).all())

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


