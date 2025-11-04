import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
from dotenv import load_dotenv
from telegram_bot import telegram_bp

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
load_dotenv()
app = Flask(__name__)
app.register_blueprint(telegram_bp)
# Use secret key from env; if missing, log a warning (Flask requires one for sessions)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24)

# Admin credentials
LOGIN_USERNAME    = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD    = os.getenv("LOGIN_PASSWORD")

# External data sources
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
UPDATES_JSON_URL  = os.getenv("UPDATES_JSON_URL")

# Ensure critical env vars are present (best-effort check)
REQUIRED_ENVS = [
    'FLASK_SECRET_KEY', 'LOGIN_USERNAME', 'LOGIN_PASSWORD',
    'ADMISSION_SCRIPT_URL', 'GOOGLE_SCRIPT_URL', 'UPDATES_JSON_URL'
]
missing = [k for k in REQUIRED_ENVS if not os.getenv(k)]
if missing:
    app.logger.warning(f"Missing recommended environment variables: {missing}")

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.route('/')
def home():
    # Fetch live updates from GitHub JSON
    updates = []
    last_updated = None
    try:
        resp = requests.get(UPDATES_JSON_URL, timeout=5)
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
@app.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        # Validate against environment variables
        if username == os.getenv('TEACHER_USERNAME') and password == os.getenv('TEACHER_PASSWORD'):
            session['logged_in'] = True
            session['role'] = 'Faculty'
            session['username'] = username
            return redirect(url_for('faculty_dashboard'))
        else:
            error = 'Invalid username or password. Please try again.'
    return render_template('faculty_login.html', role='Faculty', error=error)

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if session.get('role') != 'Faculty':
        return redirect(url_for('faculty_login'))
    return render_template('faculty_dashboard.html', username=session.get('username'))

# -- Google-Forms data display ----------------------------------
@app.route('/gfapplications')
def display_data():
    if not session.get('logged_in') :
        return redirect(url_for('login'))
    try:
        resp = requests.get(GOOGLE_SCRIPT_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"Error fetching data: {e}"
    return render_template('gfApp.html', data=data)

import pandas as pd
import requests
import os

def get_admission_dataframe():
    """Fetch admission application data from ADMISSION_SCRIPT_URL and return a DataFrame.

    Returns:
        pd.DataFrame on success, or None on failure. Callers must handle None.
    """
    try:
        admission_url = os.getenv("ADMISSION_SCRIPT_URL")
        if not admission_url:
            raise RuntimeError("ADMISSION_SCRIPT_URL not configured")
        resp = requests.get(admission_url, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data)
        # normalize column names
        df.columns = [str(col).strip() for col in df.columns]
        return df
    except Exception as e:
        app.logger.exception("Admission application fetch failed")
        return None

# -- Admission applications --------------------------------------
@app.route('/admission-applications')
def admission_applications():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        data_df = get_admission_dataframe()
        if data_df is None:
            app.logger.error('Admission data not available')
            return render_template('error.html', message='Admission data currently unavailable.')

        # defensive column selection
        for col in ['Application', 'Candidate Name', 'Rank', 'Seat Category', 'Joining']:
            if col not in data_df.columns:
                data_df[col] = ''

        student_preview = data_df[['Application', 'Candidate Name', 'Rank']].fillna('')

        # Seat statistics
        total_seats = 180
        filled_seats = data_df['Seat Category'].fillna('').astype(str).str.strip().replace('', pd.NA).dropna().shape[0]
        vacant_seats = total_seats - filled_seats

        # Sum up all installment columns
        installment_cols = [col for col in data_df.columns if 'Installment' in col]
        if installment_cols:
            total_collected = data_df[installment_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum().sum()
        else:
            total_collected = 0

        # Withdrawals and actual strength
        withdrawing_students = 0
        try:
            withdrawing_students = data_df[data_df['Joining'].astype(str).str.upper().str.strip() == 'N'].shape[0]
        except Exception:
            withdrawing_students = 0
        actual_strength = filled_seats - withdrawing_students

        student_full = data_df.fillna('').to_dict('records')

        return render_template(
            'admissionApp.html',
            student_full=student_full,  # full data
            students=student_preview.to_dict('records'),
            total_seats=total_seats,
            filled_seats=filled_seats,
            vacant_seats=vacant_seats,
            withdrawing_students=withdrawing_students,
            actual_strength=actual_strength,
            total_collected=int(total_collected)
        )
    except Exception as err:
        app.logger.exception("Admission application error")
        return render_template('error.html', message="Error loading admission data.")

@app.route('/api/student/<app_id>')
def api_view_student(app_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        app.logger.debug(f"api_view_student called for {app_id}")
        data_df = get_admission_dataframe()
        if data_df is None:
            return jsonify({'error': 'Admission data unavailable'}), 503

        try:
            # support string or numeric application ids
            if data_df['Application'].dtype == object:
                matches = data_df[data_df['Application'].astype(str) == str(app_id)]
            else:
                matches = data_df[data_df['Application'] == int(app_id)]
            student = matches.to_dict('records')
            if student:
                return jsonify(student[0])
            return jsonify({'error': 'Student not found'}), 404
        except Exception:
            app.logger.exception('Error fetching student record')
            return jsonify({'error': 'Internal server error'}), 500
    
# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
