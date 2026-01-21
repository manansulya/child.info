# ===============================
# PROFESSIONAL MULTI-FILE VERSION
# Student Management Dashboard
# Tech: Flask + SQLite + CSS (Mobile-first) + PDF Reports
# ===============================

# -------- Folder Structure --------
# student_dashboard/
# ├── app.py
# ├── database.py
# ├── auth.py
# ├── reports.py
# ├── requirements.txt
# ├── /static
# │   └── style.css
# └── /templates
#     ├── login.html
#     ├── dashboard.html
#     └── base.html

# ==================================
# app.py
# ==================================
from flask import Flask
from auth import auth_bp
from database import init_db
from reports import report_bp

app = Flask(__name__)
app.secret_key = 'change-this'

app.register_blueprint(auth_bp)
app.register_blueprint(report_bp)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

# ==================================
# database.py
# ==================================
import sqlite3

DB = 'school.db'

def get_db():
    return sqlite3.connect(DB)

def init_db():
    con = get_db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY, name TEXT)")
    cur.execute("""CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY,
        name TEXT,
        section TEXT,
        roll INTEGER,
        gender TEXT,
        notebook INTEGER,
        copy_checked INTEGER,
        projects INTEGER,
        class_id INTEGER)
    """)
    cur.execute("INSERT OR IGNORE INTO users VALUES(1,'admin','admin123','admin')")
    cur.execute("INSERT OR IGNORE INTO users VALUES(2,'teacher','teacher123','teacher')")
    con.commit()
    con.close()

# ==================================
# auth.py
# ==================================
from flask import Blueprint, render_template, request, redirect, session
from database import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        con = get_db()
        cur = con.cursor()
        cur.execute('SELECT role FROM users WHERE username=? AND password=?',(u,p))
        row = cur.fetchone()
        if row:
            session['user']=u
            session['role']=row[0]
            return redirect('/dashboard')
    return render_template('login.html')

# ==================================
# analytics.py (Graphical Marks Analytics)
# ==================================
from flask import Blueprint, render_template
from database import get_db
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

analytics_bp = Blueprint('analytics', __name__)


def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


@analytics_bp.route('/analytics')
def analytics_dashboard():
    con = get_db()
    cur = con.cursor()

    # Class-wise average marks
    cur.execute("""
        SELECT classes.name, AVG(students.marks)
        FROM classes JOIN students ON classes.id = students.class_id
        GROUP BY classes.id
    """)
    class_avg = cur.fetchall()

    # Grade distribution
    cur.execute("SELECT grade, COUNT(*) FROM students GROUP BY grade")
    grades = cur.fetchall()

    con.close()

    # Bar chart: Class-wise average
    fig1 = plt.figure()
    plt.bar([c[0] for c in class_avg], [c[1] for c in class_avg])
    plt.title('Class-wise Average Marks')
    class_bar = fig_to_base64(fig1)

    # Pie chart: Grade distribution
    fig2 = plt.figure()
    plt.pie([g[1] for g in grades], labels=[g[0] for g in grades], autopct='%1.1f%%')
    plt.title('Grade Distribution')
    grade_pie = fig_to_base64(fig2)

    return render_template('analytics.html', class_bar=class_bar, grade_pie=grade_pie)

# ==================================
# database.py (UPDATED for Marks & Grades)
# ==================================
import sqlite3
DB = 'school.db'

def get_db():
    return sqlite3.connect(DB)

def init_db():
    con = get_db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY, name TEXT)")
    cur.execute("""CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY,
        name TEXT,
        section TEXT,
        roll INTEGER,
        gender TEXT,
        notebook INTEGER,
        copy_checked INTEGER,
        projects INTEGER,
        marks INTEGER,
        grade TEXT,
        class_id INTEGER)
    """)
    con.commit(); con.close()

# ==================================
# templates/analytics.html
# ==================================
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="container">
<h2>Analytics Dashboard</h2>

<div class="card">
<h3>Class-wise Student Count</h3>
<ul>
{% for c in class_stats %}
<li>{{c[0]}} : {{c[1]}} students</li>
{% endfor %}
</ul>
</div>

<div class="card">
<h3>Student-wise Marks</h3>
<table width="100%">
<tr><th>Name</th><th>Marks</th></tr>
{% for s in student_marks %}
<tr><td>{{s[0]}}</td><td>{{s[1]}}</td></tr>
{% endfor %}
</table>
</div>
</div>
</body>
</html>

# ==================================
# static/style.css (ADD TABLE STYLES)
# ==================================
table{border-collapse:collapse}
th,td{padding:.5rem;border-bottom:1px solid #e5e7eb;text-align:left}
 (Mobile-first UI)
# ==================================
/* Mobile-first */
body{font-family:system-ui;background:#f8fafc;margin:0}
.container{padding:1rem}
.card{background:#fff;border-radius:14px;padding:1rem;margin-bottom:1rem;box-shadow:0 10px 20px rgba(0,0,0,.08)}
input,select,button{width:100%;padding:.7rem;margin:.4rem 0;border-radius:8px;border:1px solid #ddd}
button{background:#2563eb;color:#fff;border:none}

@media(min-width:768px){
  .grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}
}

# ==================================
# templates/login.html
# ==================================
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="/static/style.css"></head>
<body><div class="container">
<div class="card">
<h2>Login</h2>
<form method="post">
<input name="username" placeholder="Username">
<input name="password" type="password" placeholder="Password">
<button>Login</button>
</form>
</div></div></body></html>

# ==================================
# templates/dashboard.html
# ==================================
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="/static/style.css"></head>
<body><div class="container">
<h2>Dashboard</h2>
<a href="/report/pdf"><button>Download PDF Report</button></a>
</div></body></html>

# ==================================
# requirements.txt
# ==================================
flask
matplotlib
reportlab
