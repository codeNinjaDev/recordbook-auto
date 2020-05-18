import os
import shutil

import json
from docx import Document
from recordbook_writer import xstr, RecordbookWriter, JournalWriter
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, flash, url_for, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology
from database import *
from auth_forms import LoginForm, RegisterForm, login
from app_forms import LeadershipForm, ServiceForm, CareerForm, AwardForm, ProjectForm

# ENDPOINTS

def manager_index(db):


    leadership_experiences = Leadership.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    service_experiences = Service.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    awards = Award.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    careers =  Career.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").all()
    projects =  Project.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").order_by(Project.project_name, Project.year.desc()).all()
    print(projects)
    email = Manager.query.filter_by(id=session["manager_id"]).first().username + ".docx"
    journal = Manager.query.filter_by(id=session["manager_id"]).first().username + "journal.docx"
    try:
        os.remove(email)
        os.remove(journal)
    except:
        pass
    return render_template("index.html", user="manager", projects=projects, leadership=leadership_experiences, service=service_experiences, awards=awards, career=careers)


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
    student_leader = None
    if request.method == "POST":
        selected_user_emails = request.form.getlist("users")

        for email in selected_user_emails:
            selected_users.append(Student.query.filter_by(username=email).first())

        form_type = request.form.get("type")
        leader = request.form.get("leader")

        if leader:
            student_leader = Student.query.filter_by(username=email).first()

    leadership_form = LeadershipForm()
    service_form = ServiceForm()
    career_form = CareerForm()
    award_form = AwardForm()
    project_form = ProjectForm()

    if leadership_form.lead_submit.data and leadership_form.validate_on_submit():
        leadership = Leadership(user_id=session["manager_id"], user_type="MANAGER", year=leadership_form.year.data, activity=leadership_form.activity.data,
            role=leadership_form.role.data, level=leadership_form.level.data, duties=leadership_form.importance.data)
        db.session.add(leadership)
        for user in selected_users:
            student_form = Leadership(user_id=user.id, user_type="STUDENT", year=leadership_form.year.data, activity=leadership_form.activity.data,
            role=leadership_form.role.data, level=leadership_form.level.data, duties=leadership_form.importance.data)
            db.session.add(student_form)
    elif service_form.service_submit.data and service_form.validate_on_submit():
        service = Service(user_id=session["manager_id"], user_type="MANAGER", year=service_form.year.data, activity=service_form.activity.data,
            role=service_form.role.data, impact=service_form.importance.data)
        db.session.add(service)
        for user in selected_users:
            student_form = Service(user_id=user.id, user_type="STUDENT", year=service_form.year.data, activity=service_form.activity.data,
                role=service_form.role.data, impact=service_form.importance.data)
            db.session.add(student_form)
    elif award_form.award_submit.data and award_form.validate_on_submit():
        award = Award(user_id=session["manager_id"], user_type="MANAGER", year=award_form.year.data, level=award_form.level.data,
            recognition=award_form.recognition.data, importance=award_form.importance.data)
        db.session.add(award)

        for user in selected_users:
            student_form = Award(user_id=user.id, user_type="STUDENT", year=award_form.year.data, level=award_form.level.data,
                recognition=award_form.recognition.data, importance=award_form.importance.data)
            db.session.add(student_form)
    elif career_form.career_submit.data and career_form.validate_on_submit():
        career = Career(user_id=session["manager_id"], user_type="MANAGER", year=career_form.year.data,
            activity=career_form.activity.data, importance=career_form.importance.data)
        db.session.add(career)

        for user in selected_users:
            student_form = Career(user_id=user.id, user_type="STUDENT", year=career_form.year.data,
                activity=career_form.activity.data, importance=career_form.importance.data)
            db.session.add(student_form)

    elif project_form.project_submit.data and project_form.validate_on_submit():
        project = Project(user_id=session["manager_id"], user_type="MANAGER", project_name=project_form.project_name.data, year=project_form.year.data, hours=project_form.hours.data, activity=project_form.activity.data, importance=project_form.importance.data)
        db.session.add(project)
        for user in selected_users:
            student_form = Project(user_id=session["user_id"], user_type="STUDENT", project_name=project_form.project_name.data, year=project_form.year.data, hours=project_form.hours.data, activity=project_form.activity.data, importance=project_form.importance.data)
            db.session.add(student_form)
    else:
        return render_template("add_activity.html", leadership_form=leadership_form, service_form=service_form,
            award_form=award_form, career_form=career_form, project_form=project_form, user="manager")

    db.session.commit()

    return redirect("/manager")

def manager_generate_journal(db, session):
    curr_manager = Manager.query.filter_by(id=session["manager_id"]).first()
    journal_name = curr_manager.username + ".journal.docx"
    journal = Document()
    journal.save(journal_name)

    writer = JournalWriter(journal_name)
    project_objects = Project.query.filter_by(user_id=session["manager_id"], user_type="MANAGER").with_entities(Project.project_name).distinct()

    for project in project_objects:
        writer.create_project_table(project.project_name, Project.query.filter_by(user_id=session["manager_id"], user_type="MANAGER", project_name=project.project_name).all())
    return send_file(journal_name, as_attachment=True)

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

    login_form = LoginForm()
    # User reached route via POST (as by submitting a form via POST)
    if login_form.validate_on_submit():

        # Ensure username exists and password is correct
        if login(db, login_form, session, user_type="manager"):
            return redirect("/manager")

        return apology("invalid username and/or password", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", login_form=login_form, user="manager")

def manager_reset(request, db, session):
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        manager = Manager.query.filter_by(id=session["manager_id"]).first()

        password_hash = manager.psswd_hash
        if not check_password_hash(password_hash, request.form.get("oldPassword")):
            return render_template("reset.html", user="manager", error=True)

        manager.psswd_hash =generate_password_hash(request.form.get("newPassword"))
        db.session.commit()

        flash("Reset password")
        return redirect("/manager")

    else:
        return render_template("reset.html", user="manager", error=False)

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

def input_award(db, user, user_type="STUDENT", year="", level="", recognition="", importance=""):
    award = Award(user_id=user, user_type=user_type, year=year, level=level,
                recognition
                =recognition, importance=importance)
    db.session.add(award)
    db.session.commit()

def input_project(db, user, user_type="STUDENT", project_name="", hours="", activity="", year="", importance=""):
    project = Project(user_id=user, user_type=user_type, project_name=project_name, year=year, hours=hours, activity=activity, importance=importance)
    db.session.add(project)
    db.session.commit()

def input_career(db, user, user_type="STUDENT", year="", activity="", importance=""):
    career = Career(user_id=user, user_type=user_type, year=year,
        activity=activity, importance=importance)
    db.session.add(career)
    db.session.commit()
