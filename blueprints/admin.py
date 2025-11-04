"""Admin-related routes: dashboard, applications, data management."""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.auth_helpers import validate_admin_credentials
from utils.data_fetcher import get_admission_data, get_gf_applications, get_documents_tracking_data
import pandas as pd

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if validate_admin_credentials(username, password):
            session['logged_in'] = True
            session['role'] = 'Admin'
            session['username'] = username
            
            logger.info(f"Admin logged in: {username}")
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'Invalid credentials'
            logger.warning(f"Failed admin login attempt: {username}")
    
    return render_template('login.html', role='Admin', error=error)


@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard with links to manage applications and data."""
    if not session.get('logged_in') or session.get('role') != 'Admin':
        flash('Please log in as admin', 'warning')
        return redirect(url_for('admin.login'))
    
    return render_template('dashboard.html', role='Admin')


@admin_bp.route('/gfapplications')
def gf_applications():
    """View guest faculty applications."""
    if not session.get('logged_in') or session.get('role') != 'Admin':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.login'))
    
    try:
        data = get_gf_applications()
        if data is None:
            flash('Unable to fetch guest faculty applications', 'warning')
            return render_template('error.html', message='Data temporarily unavailable')
        
        return render_template('gfApp.html', data=data)
    except Exception as e:
        logger.exception("Error displaying GF applications")
        return render_template('error.html', message='Error loading data')


@admin_bp.route('/admission-applications')
def admission_applications():
    """View student admission applications with statistics."""
    if not session.get('logged_in') or session.get('role') != 'Admin':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.login'))
    
    try:
        data_df = get_admission_data()
        
        if data_df is None or data_df.empty:
            logger.error('Admission data not available')
            return render_template('error.html', message='Admission data currently unavailable.')
        
        # Defensive column selection
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
            student_full=student_full,
            students=student_preview.to_dict('records'),
            total_seats=total_seats,
            filled_seats=filled_seats,
            vacant_seats=vacant_seats,
            withdrawing_students=withdrawing_students,
            actual_strength=actual_strength,
            total_collected=int(total_collected)
        )
    except Exception as err:
        logger.exception("Admission application error")
        return render_template('error.html', message="Error loading admission data.")


@admin_bp.route('/api/student/<app_id>')
def api_view_student(app_id):
    """API endpoint to get student details by application ID."""
    if not session.get('logged_in') or session.get('role') != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    logger.debug(f"api_view_student called for {app_id}")
    data_df = get_admission_data()
    
    if data_df is None:
        return jsonify({'error': 'Admission data unavailable'}), 503
    
    try:
        # Support string or numeric application ids
        if data_df['Application'].dtype == object:
            matches = data_df[data_df['Application'].astype(str) == str(app_id)]
        else:
            matches = data_df[data_df['Application'] == int(app_id)]
        
        student = matches.to_dict('records')
        
        if student:
            return jsonify(student[0])
        return jsonify({'error': 'Student not found'}), 404
    except Exception:
        logger.exception('Error fetching student record')
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/documents-tracking')
def documents_tracking():
    """View documents tracking for batch 2025-26."""
    if not session.get('logged_in') or session.get('role') != 'Admin':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.login'))
    
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


@admin_bp.route('/logout')
def logout():
    """Log out admin."""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('home.landing'))
