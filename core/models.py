from core import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Student/Teacher/Admin
    roll_no = db.Column(db.String(50))  # For students
    phone = db.Column(db.String(20))  # Optional
    attendance = db.Column(db.Float, nullable=True)  # Overall attendance %

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Performance('{self.student_id}', '{self.score}', '{self.grade}')"

class StudentDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    user = db.relationship('User', backref='student_detail', lazy=True)

class TeacherDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='teacher_detail', lazy=True)

class PerformanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    score = db.Column(db.Float, nullable=False)
    attendance = db.Column(db.Integer, nullable=True)


    student = db.relationship('User', backref='performance_records')
