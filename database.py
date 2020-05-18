from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    psswd_hash = db.Column(db.String(256), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=True)
    club_name = db.Column(db.String(128), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    county = db.Column(db.String(128), nullable=True)
    district = db.Column(db.String(128), nullable=True)
    category = db.Column(db.String(128), nullable=True)
    division = db.Column(db.String(128), nullable=True)

    def __repr__(self):
            return '<User %r>' % self.username
class Manager(db.Model):
    __tablename__ = 'managers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    psswd_hash = db.Column(db.String(256), nullable=False)
    club_name = db.Column(db.String(128), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    county = db.Column(db.String(128), nullable=True)
    district = db.Column(db.String(128), nullable=True)
    def __repr__(self):
        return '<Manager %r>' % self.username

class Leadership(db.Model):
    __tablename__ = 'leaderships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(8), nullable=False)
    year = db.Column(db.String(5))
    activity = db.Column(db.String(256))
    role = db.Column(db.String(1))
    level = db.Column(db.String(2))
    duties = db.Column(db.String(256))

    def __repr__(self):
        return '<Leadership %r>' % self.activity

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(8), nullable=False)
    year = db.Column(db.String(5))
    activity = db.Column(db.String(256))
    role = db.Column(db.String(1))
    impact = db.Column(db.String(256))

    def __repr__(self):
        return '<Service %r>' % self.activity

class Award(db.Model):
    __tablename__ = 'awards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(8), nullable=False)
    year = db.Column(db.String(5))
    recognition = db.Column(db.String(256))
    level = db.Column(db.String(2))
    importance = db.Column(db.String(256))

    def __repr__(self):
        return '<Award %r>' % self.recognition

class Career(db.Model):
    __tablename__ = 'careers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(8), nullable=False)
    year = db.Column(db.String(5))
    activity = db.Column(db.String(256))
    importance = db.Column(db.String(256))

    def __repr__(self):
        return '<Career %r>' % self.activity

class Invitation(db.Model):
    __tablename__ = 'invitations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    club_name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<Manager %r>' % self.username

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(8), nullable=False)
    project_name = db.Column(db.String(128), nullable=False)
    year = db.Column(db.String(5))
    hours = db.Column(db.String(128))
    activity = db.Column(db.String(256), nullable=False)
    importance = db.Column(db.String(256))

    def __repr__(self):
        return '<Project %r>' % self.activity