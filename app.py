from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from models import db, Student, Teacher, Subject, Review, FacultyResponse
from datetime import datetime
import re
import os

app = Flask(__name__)
app.secret_key = "vcet_secret_key_2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vcet_reviews.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt = Bcrypt(app)

def time_ago(dt):
    diff = datetime.utcnow() - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins} minute{'s' if mins > 1 else ''} ago"
    elif seconds < 86400:
        hrs = seconds // 3600
        return f"{hrs} hour{'s' if hrs > 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"

def strip_html(text):
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.strip()

@app.route("/")
def home():
    return redirect(url_for("student_login"))

@app.route("/login/student", methods=["GET", "POST"])
def student_login():
    error = None
    if request.method == "POST":
        vcet_id = request.form.get("vcet_id", "").strip()
        password = request.form.get("password", "").strip()
        student = Student.query.filter_by(vcet_id=vcet_id).first()
        if student and bcrypt.check_password_hash(student.password_hash, password):
            session["user_id"] = student.id
            session["role"] = "student"
            session["name"] = student.name
            return redirect(url_for("student_portal"))
        else:
            error = "Invalid Student ID or Password. Please try again."
    return render_template("login_student.html", error=error)

@app.route("/login/teacher", methods=["GET", "POST"])
def teacher_login():
    error = None
    if request.method == "POST":
        emp_id = request.form.get("employee_id", "").strip()
        password = request.form.get("password", "").strip()
        teacher = Teacher.query.filter_by(employee_id=emp_id).first()
        if teacher and bcrypt.check_password_hash(teacher.password_hash, password):
            session["user_id"] = teacher.id
            session["role"] = "teacher"
            session["name"] = teacher.name
            return redirect(url_for("teacher_dashboard"))
        else:
            error = "Invalid Employee ID or Password. Please try again."
    return render_template("login_teacher.html", error=error)

@app.route("/portal")
def student_portal():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))

    reviews = Review.query.order_by(Review.created_at.desc()).all()
    subjects = Subject.query.all()

    # Check which subjects this student already reviewed
    student_id = session["user_id"]
    reviewed_subject_ids = [r.subject_id for r in Review.query.filter_by(student_id=student_id).all()]

    review_list = []
    for r in reviews:
        review_list.append({
            "id": r.id,
            "subject": r.subject.name,
            "rating": r.rating,
            "text": r.text,
            "time_ago": time_ago(r.created_at),
            "response": r.response.response_text if r.response else None
        })

    top_review_obj = Review.query.order_by(Review.rating.desc(), Review.created_at.desc()).first()
    top_review = None
    if top_review_obj:
        top_review = {
            "subject": top_review_obj.subject.name,
            "rating": top_review_obj.rating,
            "text": top_review_obj.text,
            "time_ago": time_ago(top_review_obj.created_at),
            "response": top_review_obj.response.response_text if top_review_obj.response else None
        }

    return render_template(
        "student_portal.html",
        reviews=review_list,
        subjects=subjects,
        top_review=top_review,
        reviewed_subject_ids=reviewed_subject_ids,
        student_name=session.get("name")
    )

@app.route("/submit-review", methods=["POST"])
def submit_review():
    if session.get("role") != "student":
        return jsonify({"error": "Unauthorized"}), 403

    subject_id = request.form.get("subject_id")
    rating = request.form.get("rating")
    text = request.form.get("text", "")
    student_id = session["user_id"]

    text = strip_html(text)

    if not subject_id or not rating or not text:
        return jsonify({"error": "All fields are required."}), 400
    if len(text) < 20 or len(text) > 500:
        return jsonify({"error": "Review must be between 20 and 500 characters."}), 400
    rating = int(rating)
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5."}), 400

    existing = Review.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if existing:
        return jsonify({"error": "You have already reviewed this subject."}), 400

    review = Review(student_id=student_id, subject_id=int(subject_id), rating=rating, text=text)
    db.session.add(review)
    db.session.commit()

    return jsonify({"success": True, "message": "Review submitted successfully!"})

@app.route("/teacher/dashboard")
def teacher_dashboard():
    if session.get("role") != "teacher":
        return redirect(url_for("teacher_login"))

    reviews = Review.query.order_by(Review.created_at.desc()).all()

    review_list = []
    for r in reviews:
        review_list.append({
            "id": r.id,
            "subject": r.subject.name,
            "subject_code": r.subject.code,
            "rating": r.rating,
            "text": r.text,
            "time_ago": time_ago(r.created_at),
            "response": r.response.response_text if r.response else None,
            "response_id": r.response.id if r.response else None,
        })

    total_reviews = len(reviews)
    no_response_count = sum(1 for r in reviews if not r.response)

    subject_stats = {}
    for r in reviews:
        name = r.subject.name
        if name not in subject_stats:
            subject_stats[name] = {"total": 0, "count": 0}
        subject_stats[name]["total"] += r.rating
        subject_stats[name]["count"] += 1
    avg_per_subject = {name: round(vals["total"] / vals["count"], 1) for name, vals in subject_stats.items()}

    return render_template(
        "teacher_dashboard.html",
        reviews=review_list,
        total_reviews=total_reviews,
        no_response_count=no_response_count,
        avg_per_subject=avg_per_subject,
        teacher_name=session.get("name")
    )

@app.route("/teacher/respond/<int:review_id>", methods=["POST"])
def teacher_respond(review_id):
    if session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 403

    teacher_id = session["user_id"]
    response_text = request.form.get("response_text", "").strip()
    response_text = strip_html(response_text)

    if not response_text or len(response_text) < 5:
        return jsonify({"error": "Response is too short."}), 400

    existing = FacultyResponse.query.filter_by(review_id=review_id).first()
    if existing:
        existing.response_text = response_text
    else:
        new_resp = FacultyResponse(review_id=review_id, teacher_id=teacher_id, response_text=response_text)
        db.session.add(new_resp)

    db.session.commit()
    return jsonify({"success": True})

@app.route("/teacher/respond/<int:review_id>/delete", methods=["POST"])
def delete_response(review_id):
    if session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 403

    resp = FacultyResponse.query.filter_by(review_id=review_id).first()
    if resp:
        db.session.delete(resp)
        db.session.commit()
    return jsonify({"success": True})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("student_login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
