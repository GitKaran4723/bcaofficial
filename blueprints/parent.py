"""Parent-related routes: login, dashboard, view student progress."""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.auth_helpers import validate_parent_credentials

logger = logging.getLogger(__name__)

parent_bp = Blueprint('parent', __name__, url_prefix='/parent')


@parent_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Parent login page."""
    error = None
    
    if request.method == 'POST':
        identifier = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # TODO: Implement actual parent authentication
        parent_info = validate_parent_credentials(identifier, password)
        
        if parent_info:
            session['role'] = 'Parent'
            session['parent_id'] = identifier
            session['parent_info'] = parent_info
            
            logger.info(f"Parent logged in: {identifier}")
            flash('Welcome, Parent!', 'success')
            return redirect(url_for('parent.dashboard'))
        else:
            error = 'Invalid credentials. Parent authentication is not yet fully implemented.'
            logger.warning(f"Failed parent login attempt: {identifier}")
    
    return render_template('parent_login.html', role='Parent', error=error)


@parent_bp.route('/dashboard')
def dashboard():
    """Parent dashboard to view student(s) progress."""
    if session.get('role') != 'Parent':
        flash('Please log in as parent', 'warning')
        return redirect(url_for('parent.login'))
    
    # TODO: Fetch linked student data
    return render_template('parent_dashboard.html')


@parent_bp.route('/logout')
def logout():
    """Log out parent."""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('home.landing'))
