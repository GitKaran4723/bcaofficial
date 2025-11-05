"""Attender-related routes: document tracking and management."""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.auth_helpers import validate_attender_credentials
from utils.data_fetcher import get_documents_tracking_data

logger = logging.getLogger(__name__)

attender_bp = Blueprint('attender', __name__, url_prefix='/attender')


@attender_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Attender login page."""
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if validate_attender_credentials(username, password):
            session['logged_in'] = True
            session['role'] = 'Attender'
            session['username'] = username

            logger.info(f"Attender logged in: {username}")
            flash('Welcome, Attender!', 'success')
            return redirect(url_for('attender.dashboard'))
        else:
            error = 'Invalid credentials'
            logger.warning(f"Failed attender login attempt: {username}")

    return render_template('login.html', role='Attender', error=error)


@attender_bp.route('/dashboard')
def dashboard():
    """Attender dashboard with access to document tracking."""
    if not session.get('logged_in') or session.get('role') != 'Attender':
        flash('Please log in as attender', 'warning')
        return redirect(url_for('attender.login'))

    return render_template('dashboard.html', role='Attender')


@attender_bp.route('/documents-tracking')
def documents_tracking():
    """View documents tracking for batch 2025-26."""
    if not session.get('logged_in') or session.get('role') != 'Attender':
        flash('Access denied', 'danger')
        return redirect(url_for('attender.login'))

    try:
        data_df = get_documents_tracking_data()

        if data_df is None or data_df.empty:
            logger.error('Documents tracking data not available')
            return render_template('error.html', message='Documents tracking data currently unavailable.')

        # Create preview data for cards (SL No., USN No, Student Name)
        student_preview = data_df[['SL No.', 'USN No', 'Student Name']].fillna('')

        # Convert full data to records for JavaScript
        student_full = data_df.fillna('').to_dict('records')

        return render_template(
            'documents_tracking.html',
            students=student_preview.to_dict('records'),
            student_full=student_full
        )
    except Exception as err:
        logger.exception("Documents tracking error")
        return render_template('error.html', message="Error loading documents tracking data.")


@attender_bp.route('/logout')
def logout():
    """Log out attender."""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('home.landing'))