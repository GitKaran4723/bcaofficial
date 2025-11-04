"""Public home/landing routes accessible to all users."""

import logging
from flask import Blueprint, render_template
from utils.data_fetcher import get_updates

logger = logging.getLogger(__name__)

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def landing():
    """Landing page with live updates/notices."""
    updates, last_updated = get_updates()
    
    return render_template('landing.html',
                          updates=updates,
                          last_updated=last_updated)


@home_bp.route('/about')
def about():
    """About page for the department."""
    return render_template('about.html')


@home_bp.route('/contact')
def contact():
    """Contact information page."""
    return render_template('contact.html')
