"""Student-related routes: login, dashboard, attendance, marks."""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.auth_helpers import validate_student_credentials

logger = logging.getLogger(__name__)

student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Student login using USN and Date of Birth."""
    error = None
    
    if request.method == 'POST':
        usn = request.form.get('usn', '').strip()
        dob = request.form.get('dob', '').strip()
        
        if not usn or not dob:
            error = 'Please provide both USN and Date of Birth'
        else:
            student_info = validate_student_credentials(usn, dob)
            
            if student_info:
                # Store student info in session
                session['role'] = 'Student'
                session['usn'] = student_info.get('USN', usn.upper())
                session['student_name'] = student_info.get('Name', student_info.get('Candidate Name', 'Student'))
                session['student_info'] = student_info
                
                logger.info(f"Student logged in: {session['usn']}")
                flash('Login successful!', 'success')
                return redirect(url_for('student.dashboard'))
            else:
                error = 'Invalid USN or Date of Birth. Please check and try again.'
                logger.warning(f"Failed login attempt for USN: {usn}")
    
    return render_template('student_login.html', error=error)


@student_bp.route('/dashboard')
def dashboard():
    """Student dashboard showing overview and quick links."""
    if session.get('role') != 'Student':
        flash('Please log in to access the student dashboard', 'warning')
        return redirect(url_for('student.login'))
    
    student_name = session.get('student_name', 'Student')
    usn = session.get('usn', '')
    
    return render_template('student_dashboard.html', 
                          student_name=student_name,
                          usn=usn)


@student_bp.route('/attendance')
def attendance():
    """View student attendance records."""
    if session.get('role') != 'Student':
        flash('Please log in to view attendance', 'warning')
        return redirect(url_for('student.login'))
    
    # TODO: Fetch actual attendance data based on student's batch/semester/section
    # For now, show placeholder
    usn = session.get('usn', '')
    student_name = session.get('student_name', 'Student')
    
    # Placeholder data structure
    attendance_data = {
        'subjects': [],
        'overall_percentage': 0
    }
    
    return render_template('student_attendance.html',
                          usn=usn,
                          student_name=student_name,
                          attendance=attendance_data)


@student_bp.route('/marks')
def marks():
    """View student internal marks/assessment results."""
    if session.get('role') != 'Student':
        flash('Please log in to view marks', 'warning')
        return redirect(url_for('student.login'))
    
    # TODO: Fetch actual marks data from Google Sheets
    usn = session.get('usn', '')
    student_name = session.get('student_name', 'Student')
    
    # Placeholder data structure
    marks_data = {
        'subjects': [],
        'total_marks': 0,
        'percentage': 0
    }
    
    return render_template('student_marks.html',
                          usn=usn,
                          student_name=student_name,
                          marks=marks_data)


@student_bp.route('/profile')
def profile():
    """View student profile with all details from Google Sheets."""
    if session.get('role') != 'Student':
        flash('Please log in to view profile', 'warning')
        return redirect(url_for('student.login'))
    
    # Get student info from session
    student_info = session.get('student_info', {})
    usn = session.get('usn', '')
    student_name = session.get('student_name', 'Student')
    
    return render_template('student_profile.html',
                          usn=usn,
                          student_name=student_name,
                          student_info=student_info)


@student_bp.route('/logout')
def logout():
    """Log out student and clear session."""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('home.landing'))
