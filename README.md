# 📝 VCET Reviews System

A full-stack anonymous student feedback platform built for **Vidyavardhini's College of Engineering and Technology (VCET), Vasai**. Students can submit honest reviews about teachers, and teachers can respond — all with secure authentication and anonymity.

🔗 **Live Demo:** [vcet-reviews.vercel.app](https://vcet-reviews.vercel.app)

---

## ✨ Features

- 🔐 **Secure Authentication** — Separate login portals for students and teachers using bcrypt password hashing
- 🕵️ **Anonymous Reviews** — Students can submit feedback without revealing their identity
- 💬 **Teacher Responses** — Teachers can view and respond to reviews about them
- 🗃️ **Database Backed** — Persistent storage using SQLAlchemy ORM
- 🌐 **Clean UI** — Fully responsive HTML/CSS frontend
- 🌱 **Seed Data** — Pre-populated database for easy testing and demo

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLAlchemy (SQLite) |
| Authentication | bcrypt |
| Frontend | HTML, CSS, Jinja2 Templates |
| Deployment | Vercel |
| Version Control | Git, GitHub |

---

## 📁 Project Structure

```
vcet_reviews/
├── app.py              # Main Flask application & routes
├── models.py           # SQLAlchemy database models
├── seed.py             # Database seeding script
├── requirements.txt    # Python dependencies
├── static/             # CSS, JS, images
│   └── css/
├── templates/          # Jinja2 HTML templates
│   ├── login/
│   │   ├── student.html
│   │   └── teacher.html
│   └── ...
└── instance/           # SQLite database (auto-generated)
```

---

## 🚀 Getting Started (Local Setup)

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PrathamMewada459/vcet_reviews.git
   cd vcet_reviews
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Seed the database**
   ```bash
   python seed.py
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 🔑 Login Portals

| Role | URL |
|---|---|
| Student | `/login/student` |
| Teacher | `/login/teacher` |

---

## 📦 Dependencies

```
Flask
Flask-SQLAlchemy
bcrypt
Werkzeug
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🙌 Built By

**Team Parallax** — First Year AIDS, VCET Vasai

| Name | GitHub |
|---|---|
| Pratham Mewada | [@PrathamMewada459](https://github.com/PrathamMewada459) |
| Vihar Makwana | [@VIHAR2212](https://github.com/VIHAR2212) |
| Pranay Patkar | [@pranay-patkar](https://github.com/pranay-patkar) |
| Varun Poojary | [@varun2507027108-oss](https://github.com/varun2507027108-oss) |
| Manthan Mertiya | — |

---

## 📄 License

This project is intended for internal institutional use at VCET, Vasai.
