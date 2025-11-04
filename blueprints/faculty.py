"""Faculty-related routes: login, dashboard, view applications."""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.auth_helpers import validate_faculty_credentials
from utils.data_fetcher import get_gf_applications, get_admission_data

logger = logging.getLogger(__name__)

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')


@faculty_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Faculty login page."""
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if validate_faculty_credentials(username, password):
            session['logged_in'] = True
            session['role'] = 'Faculty'
            session['username'] = username
            
            logger.info(f"Faculty logged in: {username}")
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('faculty.dashboard'))
        else:
            error = 'Invalid username or password. Please try again.'
            logger.warning(f"Failed faculty login attempt: {username}")
    
    return render_template('faculty_login.html', role='Faculty', error=error)


@faculty_bp.route('/dashboard')
def dashboard():
    """Faculty dashboard with links to view applications and data."""
    if session.get('role') != 'Faculty':
        flash('Please log in as faculty', 'warning')
        return redirect(url_for('faculty.login'))
    
    username = session.get('username', 'Faculty')
    return render_template('faculty_dashboard.html', username=username)


@faculty_bp.route('/gfapplications')
def gf_applications():
    """View guest faculty applications (faculty access)."""
    if session.get('role') != 'Faculty':
        flash('Access denied', 'danger')
        return redirect(url_for('faculty.login'))
    
    try:
        data = get_gf_applications()
        if data is None:
            flash('Unable to fetch guest faculty applications', 'warning')
            return render_template('error.html', message='Data temporarily unavailable')
        
        return render_template('gfApp.html', data=data)
    except Exception as e:
        logger.exception("Error displaying GF applications")
        return render_template('error.html', message='Error loading data')


@faculty_bp.route('/admission-applications')
def admission_applications():
    """View student admission applications (faculty access)."""
    if session.get('role') != 'Faculty':
        flash('Access denied', 'danger')
        return redirect(url_for('faculty.login'))
    
    # Reuse admin blueprint logic
    from blueprints.admin import admission_applications as admin_admission_view
    return admin_admission_view()


@faculty_bp.route('/logout')
def logout():
    """Log out faculty."""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('home.landing'))
