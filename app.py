import os, re, html
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, Student, Teacher, Subject, Review, FacultyResponse
import bcrypt
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vcet-secret-key-2024-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vcet_reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

VALID_DIVISIONS = {'A','B','C','D','E','G','H','I','J','K'}
VALID_BRANCHES  = {'AIDS','CE','EHTC','IT'}

# Format examples: VCET2024AIDSG001, VCET2024CEA012, VCET2024EHTCB005
STUDENT_ID_PATTERN = re.compile(
    r'^VCET\d{4}(AIDS|CE|EHTC|IT)([A-EG-KA-E]{1})\d{3}$', re.IGNORECASE
)

with app.app_context():
    db.create_all()

# ── Helpers ──────────────────────────────────────────────────────────────

def sanitize(text):
    text = html.escape(text.strip())
    text = re.sub(r'<[^>]+>', '', text)
    return text

def timeago(dt):
    diff = datetime.utcnow() - dt
    if diff.days >= 365:  return f"{diff.days // 365}y ago"
    if diff.days >= 30:   return f"{diff.days // 30}mo ago"
    if diff.days >= 1:    return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours >= 1:        return f"{hours}h ago"
    mins  = diff.seconds // 60
    return f"{mins}m ago" if mins >= 1 else "just now"

def review_to_dict(r):
    return {
        'id':           r.id,
        'subject':      r.subject.name,
        'subject_code': r.subject.code,
        'rating':       r.rating,
        'text':         r.text,
        'created_at':   timeago(r.created_at),
        'response': {
            'text':       r.response.response_text,
            'created_at': timeago(r.response.created_at)
        } if r.response else None
    }

# ── FIXED: Returns JSON for API calls, redirect for page requests ─────────
def require_student(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'student':
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated

def require_teacher(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'teacher':
            if request.is_json or request.path.startswith('/teacher/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('teacher_login'))
        return f(*args, **kwargs)
    return decorated

# ── Auth ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('student_login'))

@app.route('/login/student', methods=['GET', 'POST'])
def student_login():
    error = None
    if request.method == 'POST':
        vcet_id  = request.form.get('vcet_id', '').strip().upper()
        password = request.form.get('password', '')
        student  = Student.query.filter_by(vcet_id=vcet_id).first()
        if student and bcrypt.checkpw(password.encode(), student.password_hash.encode()):
            session.clear()
            session['role']     = 'student'
            session['user_id']  = student.id
            session['vcet_id']  = student.vcet_id
            session['division'] = getattr(student, 'division', 'G')
            session['branch']   = student.branch
            return redirect(url_for('student_portal'))
        error = 'Invalid VCET ID or password. Please check and try again.'
    return render_template('login_student.html', error=error)

@app.route('/login/teacher', methods=['GET', 'POST'])
def teacher_login():
    error = None
    if request.method == 'POST':
        emp_id   = request.form.get('employee_id', '').strip().upper()
        password = request.form.get('password', '')
        teacher  = Teacher.query.filter_by(employee_id=emp_id).first()
        if teacher and bcrypt.checkpw(password.encode(), teacher.password_hash.encode()):
            session.clear()
            session['role']         = 'teacher'
            session['user_id']      = teacher.id
            session['teacher_name'] = teacher.name
            session['teacher_dept'] = teacher.department
            return redirect(url_for('teacher_dashboard'))
        error = 'Invalid Employee ID or password. Please check and try again.'
    return render_template('login_teacher.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('student_login'))

# ── Student Portal ────────────────────────────────────────────────────────

@app.route('/portal')
@require_student
def student_portal():
    subjects = Subject.query.order_by(Subject.department, Subject.name).all()
    my_reviews = Review.query.filter_by(student_id=session['user_id']).all()
    reviewed_subject_ids = {r.subject_id for r in my_reviews}
    return render_template('student_portal.html',
                           subjects=subjects,
                           reviewed_subject_ids=reviewed_subject_ids,
                           vcet_id=session.get('vcet_id'),
                           division=session.get('division', ''),
                           branch=session.get('branch', ''))

@app.route('/submit-review', methods=['POST'])
@require_student
def submit_review():
    subject_id = request.form.get('subject_id', type=int)
    rating     = request.form.get('rating', type=int)
    text       = sanitize(request.form.get('text', ''))

    if not subject_id or not rating or not text:
        return jsonify({'error': 'All fields are required.'}), 400
    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5.'}), 400
    if len(text) < 20:
        return jsonify({'error': 'Review must be at least 20 characters.'}), 400
    if len(text) > 500:
        return jsonify({'error': 'Review must not exceed 500 characters.'}), 400

    existing = Review.query.filter_by(
        student_id=session['user_id'], subject_id=subject_id
    ).first()
    if existing:
        return jsonify({'error': 'You have already reviewed this subject.'}), 409

    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({'error': 'Subject not found.'}), 404

    review = Review(
        student_id=session['user_id'],
        subject_id=subject_id,
        rating=rating,
        text=text
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'success': True, 'review': review_to_dict(review)}), 201

@app.route('/api/reviews')
@require_student
def api_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return jsonify([review_to_dict(r) for r in reviews])

@app.route('/api/top-review')
@require_student
def api_top_review():
    top = Review.query.filter_by(rating=5).order_by(Review.created_at.desc()).first()
    if not top:
        top = Review.query.order_by(Review.rating.desc(), Review.created_at.desc()).first()
    return jsonify(review_to_dict(top) if top else None)

# ── Teacher Dashboard ─────────────────────────────────────────────────────

@app.route('/teacher/dashboard')
@require_teacher
def teacher_dashboard():
    reviews   = Review.query.order_by(Review.created_at.desc()).all()
    total     = len(reviews)
    unanswered = sum(1 for r in reviews if not r.response)

    from collections import defaultdict
    subject_stats = defaultdict(lambda: {'total': 0, 'count': 0, 'name': ''})
    for r in reviews:
        subject_stats[r.subject_id]['total'] += r.rating
        subject_stats[r.subject_id]['count'] += 1
        subject_stats[r.subject_id]['name']   = r.subject.name
    avg_stats = sorted(
        [{'name': v['name'], 'avg': round(v['total']/v['count'], 1), 'count': v['count']}
         for v in subject_stats.values()],
        key=lambda x: -x['avg']
    )

    return render_template('teacher_dashboard.html',
                           reviews=reviews,
                           total_reviews=total,
                           no_response_count=unanswered,
                           avg_per_subject={s['name']: s['avg'] for s in avg_stats},
                           teacher_name=session.get('teacher_name'),
                           teacher_dept=session.get('teacher_dept'),
                           timeago=timeago)

@app.route('/teacher/respond/<int:review_id>', methods=['POST'])
@require_teacher
def teacher_respond(review_id):
    review = Review.query.get_or_404(review_id)
    data   = request.get_json()
    text   = sanitize(data.get('text', ''))
    if not text or len(text) < 5:
        return jsonify({'error': 'Response is too short.'}), 400
    if len(text) > 1000:
        return jsonify({'error': 'Response is too long (max 1000 chars).'}), 400

    if review.response:
        review.response.response_text = text
        review.response.created_at    = datetime.utcnow()
    else:
        fr = FacultyResponse(
            review_id=review_id,
            teacher_id=session['user_id'],
            response_text=text
        )
        db.session.add(fr)
    db.session.commit()
    return jsonify({'success': True, 'text': text})

@app.route('/teacher/respond/<int:review_id>', methods=['DELETE'])
@require_teacher
def delete_response(review_id):
    review = Review.query.get_or_404(review_id)
    if review.response:
        db.session.delete(review.response)
        db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)