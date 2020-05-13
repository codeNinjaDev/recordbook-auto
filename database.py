from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    psswd_hash = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(80), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=True)
    def __repr__(self):
            return '<User %r>' % self.username
class Manager(db.Model):
    __tablename__ = 'managers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    psswd_hash = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return '<Manager %r>' % self.username