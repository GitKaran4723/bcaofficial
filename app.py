import os
from flask import Flask, render_template, request, redirect, url_for, session
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")

@app.route('/')
def home():
    return render_template("landing.html")

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
            error = 'Invalid Credentials. Try again.'
    return render_template("login.html", error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("dashboard.html")

@app.route('/gfapplications')
def display_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        data = response.json()
    except Exception as e:
        return f"Error fetching data: {e}"
    return render_template("gfApp.html", data=data)

@app.route('/admission-applications')
def admission_applications():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Placeholder for admission data
    return render_template("admissionApp.html")

if __name__ == '__main__':
    app.run(debug=True)
