"""Authentication helper functions for different user roles."""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
from utils.data_fetcher import get_student_data

logger = logging.getLogger(__name__)


def validate_admin_credentials(username: str, password: str) -> bool:
    """Validate admin login credentials against environment variables.
    
    Args:
        username: Admin username
        password: Admin password
        
    Returns:
        True if credentials match, False otherwise
    """
    admin_user = os.getenv('LOGIN_USERNAME')
    admin_pass = os.getenv('LOGIN_PASSWORD')
    
    return username == admin_user and password == admin_pass


def validate_faculty_credentials(username: str, password: str) -> bool:
    """Validate faculty login credentials against environment variables.
    
    Args:
        username: Faculty username
        password: Faculty password
        
    Returns:
        True if credentials match, False otherwise
    """
    faculty_user = os.getenv('TEACHER_USERNAME')
    faculty_pass = os.getenv('TEACHER_PASSWORD')
    
    return username == faculty_user and password == faculty_pass


def validate_student_credentials(usn: str, dob: str) -> Optional[Dict[str, Any]]:
    """Validate student credentials using USN and Date of Birth.
    
    The function fetches student data from Google Sheets and validates
    the USN and DOB combination. DOB can be in various formats.
    
    Args:
        usn: University Seat Number (case-insensitive)
        dob: Date of Birth (formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY)
        
    Returns:
        Dict with student information if valid, None otherwise
    """
    try:
        # Fetch student data
        df = get_student_data()
        
        if df is None or df.empty:
            logger.error("Student data not available for authentication")
            return None
        
        # Normalize USN (uppercase, strip whitespace)
        usn_normalized = str(usn).strip().upper()
        
        # Try to find the USN column (common variations)
        usn_col = None
        for col in df.columns:
            col_lower = str(col).lower()
            if 'usn' in col_lower or 'seat' in col_lower or 'id' in col_lower:
                usn_col = col
                break
        
        if usn_col is None:
            logger.error("USN column not found in student data")
            return None
        
        # Find DOB column (common variations)
        dob_col = None
        for col in df.columns:
            col_lower = str(col).lower()
            if 'dob' in col_lower or 'birth' in col_lower or 'date of birth' in col_lower:
                dob_col = col
                break
        
        if dob_col is None:
            logger.error("DOB column not found in student data")
            return None
        
        # Filter by USN
        student_rows = df[df[usn_col].astype(str).str.strip().str.upper() == usn_normalized]
        
        if student_rows.empty:
            logger.warning(f"USN not found: {usn_normalized}")
            return None
        
        student = student_rows.iloc[0]
        
        # Validate DOB
        student_dob = student[dob_col]
        
        if pd.isna(student_dob):
            logger.warning(f"DOB not set for USN: {usn_normalized}")
            return None
        
        # Normalize DOB for comparison
        if not validate_dob_match(student_dob, dob):
            logger.warning(f"DOB mismatch for USN: {usn_normalized}")
            return None
        
        # Return student info as dict
        student_info = student.to_dict()
        student_info['USN'] = usn_normalized  # Ensure normalized USN is stored
        
        return student_info
        
    except Exception as e:
        logger.exception("Error validating student credentials")
        return None


def validate_dob_match(stored_dob: Any, input_dob: str) -> bool:
    """Compare two date values, handling various formats.
    
    Args:
        stored_dob: DOB from database (can be string, datetime, or Timestamp)
        input_dob: User input DOB string
        
    Returns:
        True if dates match, False otherwise
    """
    try:
        # Parse stored DOB
        if isinstance(stored_dob, (datetime, pd.Timestamp)):
            stored_date = stored_dob.date()
        else:
            # Try common date formats
            stored_str = str(stored_dob).strip()
            stored_date = parse_date_string(stored_str)
            
            if stored_date is None:
                return False
        
        # Parse input DOB
        input_date = parse_date_string(input_dob)
        
        if input_date is None:
            return False
        
        return stored_date == input_date
        
    except Exception as e:
        logger.exception("Error comparing DOB values")
        return False


def parse_date_string(date_str: str) -> Optional[datetime.date]:
    """Parse date string in common formats.
    
    Supported formats:
    - YYYY-MM-DD
    - DD/MM/YYYY
    - DD-MM-YYYY
    - MM/DD/YYYY
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime.date object or None if parsing fails
    """
    date_str = str(date_str).strip()
    
    # Try common formats
    formats = [
        '%Y-%m-%d',      # 2000-01-15
        '%d/%m/%Y',      # 15/01/2000
        '%d-%m-%Y',      # 15-01-2000
        '%m/%d/%Y',      # 01/15/2000
        '%Y/%m/%d',      # 2000/01/15
        '%d.%m.%Y',      # 15.01.2000
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    logger.debug(f"Could not parse date: {date_str}")
    return None


def validate_parent_credentials(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    """Validate parent login credentials.
    
    TODO: Implement parent authentication logic.
    For now, this is a placeholder.
    
    Args:
        identifier: Parent email or phone
        password: Parent password
        
    Returns:
        Dict with parent information if valid, None otherwise
    """
    # TODO: Implement parent authentication
    logger.warning("Parent authentication not yet implemented")
    return None
