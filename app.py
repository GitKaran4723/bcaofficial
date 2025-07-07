import os
from flask import Flask, render_template, request, redirect, url_for, session
import requests
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Admin credentials
LOGIN_USERNAME    = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD    = os.getenv("LOGIN_PASSWORD")

# External data sources
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
UPDATES_JSON_URL  = os.getenv("UPDATES_JSON_URL")

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.route('/')
def home():
    # Fetch live updates from GitHub JSON
    updates = []
    last_updated = None
    try:
        resp = requests.get(UPDATES_JSON_URL, timeout=3)
        resp.raise_for_status()
        payload = resp.json()
        updates = payload.get("updates", [])
        last_updated = payload.get("last_updated")
    except Exception as e:
        app.logger.warning(f"Could not fetch live updates: {e}")

    return render_template('landing.html',
                           updates=updates,
                           last_updated=last_updated)

# -- Admin login (shared) ---------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials'
    return render_template('login.html', role='Admin', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', role='Admin')

# -- Student login ------------------------------------------------
@app.route('/student/login', methods=['GET','POST'])
def student_login():
    error = None
    if request.method == 'POST':
        # TODO: validate student credentials
        session['role'] = 'Student'
        return redirect(url_for('student_dashboard'))
    return render_template('student_login.html', role='Student', error=error)

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'Student':
        return redirect(url_for('student_login'))
    return render_template('student_dashboard.html')

# -- Parent login -------------------------------------------------
@app.route('/parent/login', methods=['GET','POST'])
def parent_login():
    error = None
    if request.method == 'POST':
        # TODO: validate parent credentials
        session['role'] = 'Parent'
        return redirect(url_for('parent_dashboard'))
    return render_template('parent_login.html', role='Parent', error=error)

@app.route('/parent/dashboard')
def parent_dashboard():
    if session.get('role') != 'Parent':
        return redirect(url_for('parent_login'))
    return render_template('parent_dashboard.html')

# -- Faculty login ------------------------------------------------
@app.route('/faculty/login', methods=['GET','POST'])
def faculty_login():
    error = None
    if request.method == 'POST':
        # TODO: validate faculty credentials
        session['role'] = 'Faculty'
        return redirect(url_for('faculty_dashboard'))
    return render_template('faculty_login.html', role='Faculty', error=error)

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if session.get('role') != 'Faculty':
        return redirect(url_for('faculty_login'))
    return render_template('faculty_dashboard.html')

# -- Google-Forms data display ----------------------------------
@app.route('/gfapplications')
def display_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        resp = requests.get(GOOGLE_SCRIPT_URL, timeout=3)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"Error fetching data: {e}"
    return render_template('gfApp.html', data=data)

# -- Admission applications --------------------------------------
@app.route('/admission-applications')
def admission_applications():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admissionApp.html')

# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
