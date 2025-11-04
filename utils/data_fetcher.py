"""Utility functions for fetching data from Google Sheets via Apps Script endpoints."""

import os
import logging
from typing import Optional, List, Dict, Any
from functools import lru_cache
import requests
import pandas as pd

logger = logging.getLogger(__name__)

# Cache timeout in seconds (5 minutes)
CACHE_TTL = 300


def fetch_json_from_url(url: str, timeout: int = 6) -> Optional[List[Dict[str, Any]]]:
    """Fetch JSON data from a URL with error handling.
    
    Args:
        url: The URL to fetch from
        timeout: Request timeout in seconds
        
    Returns:
        List of dictionaries on success, None on failure
    """
    try:
        if not url:
            logger.warning("fetch_json_from_url called with empty URL")
            return None
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, list):
            logger.warning(f"Expected list from {url}, got {type(data)}")
            return None
            
        return data
    except requests.RequestException as e:
        logger.exception(f"Failed to fetch data from {url}")
        return None
    except ValueError as e:
        logger.exception(f"Failed to parse JSON from {url}")
        return None


def get_student_data() -> Optional[pd.DataFrame]:
    """Fetch student login data from Google Sheets.
    
    Returns:
        DataFrame with student data or None on failure
    """
    url = os.getenv('STUDENT_DATA_for_login')
    data = fetch_json_from_url(url)
    
    if data is None:
        return None
    
    try:
        df = pd.DataFrame(data)
        # Normalize column names (strip whitespace)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    except Exception as e:
        logger.exception("Failed to create DataFrame from student data")
        return None


def get_admission_data() -> Optional[pd.DataFrame]:
    """Fetch admission application data from Google Sheets.
    
    Returns:
        DataFrame with admission data or None on failure
    """
    url = os.getenv('ADMISSION_SCRIPT_URL')
    data = fetch_json_from_url(url)
    
    if data is None:
        return None
    
    try:
        df = pd.DataFrame(data)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    except Exception as e:
        logger.exception("Failed to create DataFrame from admission data")
        return None


def get_gf_applications() -> Optional[List[Dict[str, Any]]]:
    """Fetch guest faculty applications from Google Sheets.
    
    Returns:
        List of application records or None on failure
    """
    url = os.getenv('GOOGLE_SCRIPT_URL')
    return fetch_json_from_url(url)


def get_updates() -> tuple[List[Dict[str, Any]], Optional[str]]:
    """Fetch live updates/notices from GitHub JSON.
    
    Returns:
        Tuple of (updates_list, last_updated_timestamp)
    """
    url = os.getenv('UPDATES_JSON_URL')
    try:
        if not url:
            return [], None
            
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        payload = response.json()
        
        updates = payload.get('updates', [])
        last_updated = payload.get('last_updated')
        
        return updates, last_updated
    except Exception as e:
        logger.warning(f"Could not fetch live updates: {e}")
        return [], None


def get_attendance_data(batch: str, semester: str, section: str, subject: str) -> Optional[List[List[Any]]]:
    """Fetch attendance data for specific batch/semester/section/subject.
    
    Args:
        batch: Student batch (e.g., '24-27')
        semester: Semester number
        section: Section letter
        subject: Subject code
        
    Returns:
        2D list (rows) with attendance data or None on failure
    """
    url = os.getenv('ATTENDANCE_Script')
    if not url:
        logger.error("ATTENDANCE_Script URL not configured")
        return None
    
    params = {
        'batch': batch,
        'semester': semester,
        'section': section,
        'subject': subject
    }
    
    try:
        response = requests.get(url, params=params, timeout=6)
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, list):
            logger.warning(f"Expected list from attendance API, got {type(data)}")
            return None
            
        return data
    except Exception as e:
        logger.exception("Failed to fetch attendance data")
        return None
