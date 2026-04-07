from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = "students"
    id            = db.Column(db.Integer, primary_key=True)
    vcet_id       = db.Column(db.String(50), unique=True, nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    branch        = db.Column(db.String(50))
    division      = db.Column(db.String(5), nullable=False, default='G')  # ← ADDED
    year          = db.Column(db.Integer)
    password_hash = db.Column(db.String(200), nullable=False)
    reviews       = db.relationship("Review", backref="student", lazy=True)

class Teacher(db.Model):
    __tablename__ = "teachers"
    id            = db.Column(db.Integer, primary_key=True)
    employee_id   = db.Column(db.String(50), unique=True, nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    department    = db.Column(db.String(50))
    password_hash = db.Column(db.String(200), nullable=False)
    responses     = db.relationship("FacultyResponse", backref="teacher", lazy=True)

class Subject(db.Model):
    __tablename__ = "subjects"
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    code       = db.Column(db.String(20))
    department = db.Column(db.String(50))
    reviews    = db.relationship("Review", backref="subject", lazy=True)

class Review(db.Model):
    __tablename__ = "reviews"
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    rating     = db.Column(db.Integer, nullable=False)
    text       = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    response   = db.relationship("FacultyResponse", backref="review", uselist=False)

class FacultyResponse(db.Model):
    __tablename__ = "faculty_responses"
    id            = db.Column(db.Integer, primary_key=True)
    review_id     = db.Column(db.Integer, db.ForeignKey("reviews.id"), nullable=False)
    teacher_id    = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=False)
    response_text = db.Column(db.String(1000), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)