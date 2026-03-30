from app import app, db
from models import Student, Teacher, Subject, Review
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

bcrypt = Bcrypt(app)

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Divisions A to K (no F): A B C D E G H I J K
        student_names = [
            "Aarav Shah", "Priya Mehta", "Rohan Desai", "Sneha Patil",
            "Karan Joshi", "Ananya Nair", "Vivek Rao", "Deepa Kulkarni",
            "Mihir Thakur", "Pooja Sawant"
        ]

        students = []
       
        for i in range(1, 11):
            roll = str(i).zfill(3)
            vcet_id = f"VCET2024AIDSG{roll}"
            pw = bcrypt.generate_password_hash("student123").decode("utf-8")
            s = Student(
                vcet_id=vcet_id,
                name=student_names[i - 1],
                branch="AIDS",
                year=2024,
                password_hash=pw
            )
            db.session.add(s)
            students.append(s)

        
        other_students = [
            ("VCET2024CEA001",    "Arjun Sharma",  "CE"),
            ("VCET2024ITB001",    "Neha Gupta",    "IT"),
            ("VCET2024EHTCC001",  "Sameer Khan",   "EHTC"),
        ]
        for vcet_id, name, branch in other_students:
            pw = bcrypt.generate_password_hash("student123").decode("utf-8")
            s = Student(vcet_id=vcet_id, name=name, branch=branch, year=2024, password_hash=pw)
            db.session.add(s)
            students.append(s)

        db.session.commit()

        teacher_data = [
            ("VCETF001", "Mrs. Anaitha Pereira",  "Mathematics"),
            ("VCETF002", "Dr. Kavita Churi",       "Physics"),
            ("VCETF003", "Ms. Beauty Ansari",      "Chemistry"),
            ("VCETF004", "Mr. Ronak Joshi",        "Program Core"),
            ("VCETF005", "Mr. Dipak Choudhari",    "Engineering"),
            ("VCETF006", "Dr. Aashi Cynth",        "Humanities"),
            ("VCETF007", "Mrs. Prachi Shah",       "Computer Science"),
            ("VCETF008", "Ms. Taranab Joshi",      "Electronics"),
            ("VCETF009", "Mrs. Shiteja Gharat",    "Information Technology"),
        ]
        teachers = []
        for emp_id, name, dept in teacher_data:
            pw = bcrypt.generate_password_hash("teacher123").decode("utf-8")
            t = Teacher(employee_id=emp_id, name=name, department=dept, password_hash=pw)
            db.session.add(t)
            teachers.append(t)
        db.session.commit()

       
        subject_data = [

            # ── COMMON / FIRST YEAR (All branches, Division G) ──
            ("Applied Mathematics",                  "AM101",    "Mathematics"),
            ("Elective Physics",                     "EP101",    "Physics"),
            ("Elective Chemistry",                   "EC101",    "Chemistry"),
            ("Program Core Course",                  "PCC101",   "Core"),
            ("Engineering Graphics",                 "EG101",    "Engineering"),
            ("Indian Knowledge System",              "IKS101",   "Humanities"),
            ("Engineering Workshop",                 "EW101",    "Engineering"),
            ("Python Programming",                   "PP101",    "Computer Science"),
            ("Social Science and Community Service", "SSCS101",  "Humanities"),

            # ── AIDS — Artificial Intelligence and Data Science ──
            ("Machine Learning",                     "AIDS301",  "AIDS"),
            ("Data Structures and Algorithms",       "AIDS201",  "AIDS"),
            ("Artificial Intelligence",              "AIDS401",  "AIDS"),
            ("Statistics for Data Science",          "AIDS302",  "AIDS"),
            ("Deep Learning",                        "AIDS501",  "AIDS"),
            ("Natural Language Processing",          "AIDS502",  "AIDS"),

            # ── CE — Computer Engineering (CADCIS / CS & DS) ──
            ("Object Oriented Programming",          "CE201",    "CE"),
            ("Operating Systems",                    "CE301",    "CE"),
            ("Computer Networks",                    "CE401",    "CE"),
            ("Database Management Systems",          "CE302",    "CE"),
            ("Software Engineering",                 "CE402",    "CE"),
            ("Theory of Computation",                "CE403",    "CE"),
            ("Data Science with Python",             "CE501",    "CE"),

            # ── IT — Information Technology ──
            ("Web Technology",                       "IT301",    "IT"),
            ("Cloud Computing",                      "IT501",    "IT"),
            ("Cyber Security",                       "IT401",    "IT"),
            ("Internet of Things",                   "IT502",    "IT"),
            ("Mobile Application Development",       "IT402",    "IT"),
            ("Computer Organization",                "IT201",    "IT"),

            # ── EHTC — Electronics and Telecommunication ──
            ("Analog Electronics",                   "EHTC201",  "EHTC"),
            ("Digital Electronics",                  "EHTC301",  "EHTC"),
            ("Signals and Systems",                  "EHTC302",  "EHTC"),
            ("Microprocessors and Microcontrollers", "EHTC401",  "EHTC"),
            ("Communication Systems",                "EHTC402",  "EHTC"),
            ("VLSI Design",                          "EHTC501",  "EHTC"),
            ("Embedded Systems",                     "EHTC502",  "EHTC"),

            # ── Mechanical ──
            ("Engineering Mechanics",                "MECH201",  "Mechanical"),
            ("Thermodynamics",                       "MECH301",  "Mechanical"),
            ("Fluid Mechanics",                      "MECH302",  "Mechanical"),
            ("Manufacturing Processes",              "MECH401",  "Mechanical"),

            # ── Electrical ──
            ("Basic Electrical Engineering",         "EE101",    "Electrical"),
            ("Electrical Machines",                  "EE301",    "Electrical"),
            ("Power Systems",                        "EE401",    "Electrical"),
            ("Control Systems",                      "EE402",    "Electrical"),
        ]

        subjects = []
        for name, code, dept in subject_data:
            sub = Subject(name=name, code=code, department=dept)
            db.session.add(sub)
            subjects.append(sub)
        db.session.commit()

       
        sub_map = {s.name: s for s in subjects}

        
        sample_reviews = [
            (
                students[0],
                sub_map["Applied Mathematics"],
                5,
                "Mrs. Anaitha Pereira explains every concept so clearly. Her teaching style makes even the toughest calculus problems easy to understand. Best maths teacher!",
                datetime.utcnow() - timedelta(days=4)
            ),
            (
                students[1],
                sub_map["Python Programming"],
                5,
                "Mrs. Prachi Shah makes Python so fun and beginner-friendly. The practical sessions are very helpful and she always encourages us to try new things.",
                datetime.utcnow() - timedelta(days=3)
            ),
            (
                students[2],
                sub_map["Elective Physics"],
                4,
                "Dr. Kavita Shuri teaches physics with very good real-world examples. The concepts are clear but the pace is sometimes a bit fast for everyone to follow.",
                datetime.utcnow() - timedelta(days=2)
            ),
            (
                students[3],
                sub_map["Engineering Graphics"],
                4,
                "Mr. Dipak Choudhari is very patient in explaining drawings and projections. Engineering Graphics is tough but the classes are very well structured.",
                datetime.utcnow() - timedelta(days=1)
            ),
            (
                students[4],
                sub_map["Indian Knowledge System"],
                3,
                "Dr. Aashi Syant covers interesting topics about Indian heritage and ancient sciences. Would be better with more interactive discussions in class.",
                datetime.utcnow() - timedelta(hours=8)
            ),
        ]

        for student, subject, rating, text, created_at in sample_reviews:
            r = Review(
                student_id=student.id,
                subject_id=subject.id,
                rating=rating,
                text=text,
                created_at=created_at
            )
            db.session.add(r)
        db.session.commit()

        print("")
        print("=" * 60)
        print("   VCET Review System — Database Seeded Successfully!")
        print("=" * 60)
        print("")
        print("  STUDENT LOGINS (Division G — AIDS):")
        print("  IDs: VCET2024AIDSG001 to VCET2024AIDSG010")
        print("  Password: student123")
        print("")
        print("  TEACHER LOGINS (Division G Faculty):")
        print("  VCETF001 — Mrs. Anaitha Pereira   | teacher123")
        print("  VCETF002 — Dr. Kavita Churi        | teacher123")
        print("  VCETF003 — Ms. Beauty Ansari       | teacher123")
        print("  VCETF004 — Mr. Ronak Joshi         | teacher123")
        print("  VCETF005 — Mr. Dipak Choudhari     | teacher123")
        print("  VCETF006 — Dr. Aashi Cynth         | teacher123")
        print("  VCETF007 — Mrs. Prachi Shah        | teacher123")
        print("  VCETF008 — Ms. Taranab Joshi       | teacher123")
        print("  VCETF009 — Mrs. Shiteja Gharat     | teacher123")
        print("")
        print("  DIVISIONS: A, B, C, D, E, G, H, I, J, K  (no F)")
        print("  BRANCHES:  AIDS | CE (CADCIS) | EHTC | IT")
        print("=" * 60)
        print("")

if __name__ == "__main__":
    seed_database()
