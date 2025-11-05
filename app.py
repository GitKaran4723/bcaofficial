"""Main Flask application with modular blueprint architecture."""

import os
import logging
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Debug mode from environment (default: True for development)
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'true').lower() in ('1', 'true', 'yes')

# Validate critical environment variables
REQUIRED_ENVS = [
    'FLASK_SECRET_KEY',
    'LOGIN_USERNAME',
    'LOGIN_PASSWORD',
    'TEACHER_USERNAME',
    'TEACHER_PASSWORD',
    'ADMISSION_SCRIPT_URL',
    'GOOGLE_SCRIPT_URL',
    'UPDATES_JSON_URL',
    'STUDENT_DATA_for_login'
]

missing = [k for k in REQUIRED_ENVS if not os.getenv(k)]
if missing:
    logger.warning(f"Missing recommended environment variables: {missing}")

# Import and register blueprints
from blueprints.home import home_bp
from blueprints.student import student_bp
from blueprints.parent import parent_bp
from blueprints.faculty import faculty_bp
from blueprints.admin import admin_bp
from blueprints.attender import attender_bp
from telegram_bot import telegram_bp

app.register_blueprint(home_bp)
app.register_blueprint(student_bp)
app.register_blueprint(parent_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(attender_bp)
app.register_blueprint(telegram_bp)

logger.info("All blueprints registered successfully")

# Legacy route redirects for backward compatibility
from flask import redirect, url_for

@app.route('/login')
def legacy_login():
    """Redirect old /login to admin login."""
    return redirect(url_for('admin.login'))

@app.route('/logout')
def legacy_logout():
    """Redirect old /logout to home."""
    return redirect(url_for('home.landing'))

@app.route('/gfapplications')
def legacy_gf():
    """Redirect old /gfapplications to admin route."""
    return redirect(url_for('admin.gf_applications'))

@app.route('/admission-applications')
def legacy_admission():
    """Redirect old /admission-applications to admin route."""
    return redirect(url_for('admin.admission_applications'))

@app.route('/api/student/<app_id>')
def legacy_api_student(app_id):
    """Redirect old API route to admin route."""
    return redirect(url_for('admin.api_view_student', app_id=app_id))

# Error handlers
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    from flask import render_template
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    from flask import render_template
    logger.exception("Internal server error")
    return render_template('error.html', message='Internal server error'), 500

# Run application
if __name__ == '__main__':
    logger.info(f"Starting Flask app in {'DEBUG' if DEBUG_MODE else 'PRODUCTION'} mode")
    app.run(debug=DEBUG_MODE, host='0.0.0.0', port=5000)
