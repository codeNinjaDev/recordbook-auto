from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from werkzeug.security import check_password_hash, generate_password_hash

from database import db, Student, Manager

class RegisterForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.InputRequired()])
    password = PasswordField('New Password', [validators.InputRequired(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])

def login(db, login_form, session, user_type="student"):
    user = None
    if user_type == "student":
        user = Student.query.filter_by(username=login_form.email.data).first()
    else:
        user = Manager.query.filter_by(username=login_form.email.data).first()

    if not user or not check_password_hash(user.psswd_hash, login_form.password.data):
        print(login_form.password.data)
        return False

    if user_type == "student":
        session["user_id"] = user.id
    else:
        session["manager_id"] = user.id
    return True