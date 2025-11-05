# BCA Department Portal - Complete Documentation

> Official web portal for the BCA Department at Bangalore University
> Version: 2.0 | Last Updated: November 2025

---

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Features](#features)
4. [Architecture](#architecture)
5. [Setup & Installation](#setup--installation)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [Development](#development)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Overview

A modular Flask-based web application providing secure access for students, parents, faculty, administrators, and attenders. The portal integrates with Google Sheets for real-time data management and supports multiple authentication flows.

### Tech Stack
- **Backend**: Flask 3.1.1 (Python)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Data Source**: Google Sheets via Apps Script
- **Additional**: Python-docx for document generation, Pandas for data processing

---

## Quick Start

### Get Running in 5 Minutes

```bash
# 1. Navigate to project
cd c:\Users\LENOVO\Desktop\gitprojects\bcaofficial

# 2. Create virtual environment (if not exists)
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\Activate.ps1  # Windows PowerShell

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
python app.py
```

Visit: http://localhost:5000

---

## Features

### 👨‍🎓 For Students
- ✅ **Secure Login**: Authenticate using USN and Date of Birth
- 📊 **Attendance Tracking**: View subject-wise and overall attendance
- 📝 **Internal Marks**: Check internal assessment scores
- 👤 **Profile View**: Complete student information display
- 📢 **Live Notices**: Department announcements

### 👨‍🏫 For Faculty
- 📋 **Applications Management**: View guest faculty applications
- 👨‍🎓 **Admission Data**: Access student admission information
- 📊 **Teaching Records**: Monthly/weekly bills with claiming hours
- 💼 **DOCX Export**: Generate professional bill reports

### 🔧 For Administrators
- 📈 **Full Dashboard**: Access to all applications and data
- 📊 **Statistics**: Admission analytics and fee tracking
- 📄 **Documents Tracking**: Monitor student document submission (batch 2025-26)
- 👥 **User Management**: Manage all portal users

### 📋 For Attenders
- 📄 **Documents Tracking**: View and track student document status
- ✓ **Document Collection**: Print collection sheets
- 🔍 **Search & Filter**: By status, section, quota

### 👪 For Parents
- 👪 **Student Progress**: View linked student information
- 📊 **Attendance & Marks**: Monitor child's academic performance

---

## Architecture

### Project Structure
```
bcaofficial/
├── app.py                          # Main Flask application entry point
├── .env                            # Environment variables (credentials, URLs)
├── requirements.txt                # Python dependencies
│
├── blueprints/                     # Modular route handlers
│   ├── __init__.py
│   ├── admin.py                    # Admin routes & dashboard
│   ├── attender.py                 # Attender document tracking
│   ├── faculty.py                  # Faculty dashboard & bills
│   ├── home.py                     # Public landing pages
│   ├── parent.py                   # Parent routes
│   └── student.py                  # Student login, dashboard, attendance, marks
│
├── utils/                          # Shared utilities
│   ├── __init__.py
│   ├── auth_helpers.py             # Authentication & validation
│   ├── data_fetcher.py             # Google Sheets data fetching
│   └── faculty_bills_helpers.py    # Bills processing logic
│
└── templates/                      # HTML templates
    ├── landing.html                # Main landing page with role selector
    ├── login.html                  # Dynamic login page (admin/faculty/attender)
    ├── error.html                  # Error display page
    │
    ├── dashboard.html              # Admin/Attender dashboard
    ├── admissionApp.html           # Admission applications view
    ├── gfApp.html                  # Guest faculty applications
    ├── documents_tracking.html     # Document tracking interface
    │
    ├── faculty_login.html          # Faculty specific login
    ├── faculty_dashboard.html      # Faculty dashboard
    ├── faculty_bills.html          # Teaching records & bills
    │
    ├── student_login.html          # Student login
    ├── student_dashboard.html      # Student dashboard
    ├── student_attendance.html     # Attendance view
    ├── student_marks.html          # Internal marks view
    ├── student_profile.html        # Student profile
    │
    ├── parent_login.html           # Parent login
    └── parent_dashboard.html       # Parent dashboard
```

### Key Design Principles
1. **Modular Blueprints**: Separate routes by user role
2. **DRY (Don't Repeat Yourself)**: Shared utilities for common tasks
3. **Security First**: Session-based auth with role validation
4. **Error Handling**: Graceful fallbacks for API failures
5. **Responsive Design**: Tailwind CSS for mobile-friendly UI

---

## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Google Apps Script endpoints configured
- Active internet connection

### Installation Steps

#### 1. Clone Repository
```bash
git clone https://github.com/GitKaran4723/bcaofficial.git
cd bcaofficial
```

#### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create `.env` file in project root:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here

# Admin Credentials
LOGIN_USERNAME=admin
LOGIN_PASSWORD=admin123

# Faculty Credentials
TEACHER_USERNAME=karan
TEACHER_PASSWORD=karan135

# Attender Credentials
ATTENDER_USERNAME=shankar
ATTENDER_PASSWORD=shankar123

# Google Apps Script URLs
STUDENT_DATA_for_login=https://script.google.com/macros/s/.../exec
ADMISSION_SCRIPT_URL=https://script.google.com/macros/s/.../exec
GOOGLE_SCRIPT_URL=https://script.google.com/macros/s/.../exec
ATTENDANCE_Script=https://script.google.com/macros/s/.../exec
STUDENTS_DOCUMENT_SCripts=https://script.google.com/macros/s/.../exec
FACULTY_BILLS_SCRIPT=https://script.google.com/macros/s/.../exec

# Updates & Notices
UPDATES_JSON_URL=https://raw.githubusercontent.com/.../updates.json

# Telegram Bot (Optional)
TELEGRAM_token=your-bot-token
```

#### 5. Run Application
```bash
python app.py
```

Server starts at: http://localhost:5000

---

## Configuration

### Required Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `FLASK_SECRET_KEY` | Session encryption | `someverysecretkey` |
| `LOGIN_USERNAME` | Admin username | `admin` |
| `LOGIN_PASSWORD` | Admin password | `admin123` |
| `TEACHER_USERNAME` | Faculty username | `karan` |
| `TEACHER_PASSWORD` | Faculty password | `karan135` |
| `ATTENDER_USERNAME` | Attender username | `shankar` |
| `ATTENDER_PASSWORD` | Attender password | `shankar123` |
| `STUDENT_DATA_for_login` | Student login data URL | Google Script URL |
| `ADMISSION_SCRIPT_URL` | Admission data URL | Google Script URL |
| `STUDENTS_DOCUMENT_SCripts` | Document tracking URL | Google Script URL |
| `FACULTY_BILLS_SCRIPT` | Teaching records URL | Google Script URL |

### Google Sheets Setup

#### Required Sheets Structure

**1. FULL_STUDENTS (Login Data)**
```
Columns: USN, Name, DOB, Batch, Semester, Section, Category, Email, Phone
```

**2. ADMISSION_DATA**
```
Columns: Application ID, Name, Rank, Category, Seat Type, Fees Status
```

**3. ATTENDANCE**
```
Columns: USN, Name, Subject, Total Classes, Attended, Percentage
```

**4. MARKS**
```
Columns: USN, Subject, IA1, IA2, IA3, Total
```

**5. DOCUMENTS_TRACKING**
```
Columns: USN, Name, Section, Quota, Document1_Status, Document2_Status, ...
```

**6. FACULTY_BILLS**
```
Columns: Date, Faculty, Dairy No., Particulars, Subject, Class, Actual hours, Subject code
```

---

## Usage Guide

### Login Credentials

#### Admin Login
- URL: http://localhost:5000/admin/login
- Username: `admin` (from .env)
- Password: `admin` (from .env)

#### Faculty Login
- URL: http://localhost:5000/faculty/login
- Username: `karan` (from .env)
- Password: `karan` (from .env)

#### Attender Login
- URL: http://localhost:5000/attender/login
- Username: `shankar` (from .env)
- Password: `shankar` (from .env)

#### Student Login
- URL: http://localhost:5000/student/login
- USN: From student database
- DOB: Format YYYY-MM-DD or DD/MM/YYYY

### Key Features Usage

#### Documents Tracking (Admin/Attender)
1. Navigate to Documents Tracking from dashboard
2. Search students by name/USN
3. Filter by Status (Complete/Pending/Not Submitted)
4. Filter by Section (A/B) and Quota (GM/SC/ST/etc.)
5. Click student row to view document modal
6. Print collection sheets using Print button

#### Faculty Bills (Faculty Only)
1. Navigate to "Teaching Records" from faculty dashboard
2. Select Faculty from dropdown (or "All")
3. Select Month from dropdown
4. View weekly tables with actual/claiming hours
5. Download DOCX report using download button

#### Student Features
1. **Dashboard**: Overview with attendance and marks cards
2. **Attendance**: Subject-wise attendance with percentages
3. **Internal Marks**: IA1, IA2, IA3 scores
4. **Profile**: Complete student information

---

## Development

### Adding New Routes

#### 1. Choose Blueprint
Select appropriate blueprint based on user role:
- `blueprints/student.py`
- `blueprints/faculty.py`
- `blueprints/admin.py`
- `blueprints/attender.py`
- `blueprints/home.py`

#### 2. Add Route Function
```python
@student_bp.route('/my-new-page')
def my_new_page():
    # Check authentication
    if session.get('role') != 'Student':
        return redirect(url_for('student.login'))
    
    # Fetch data
    data = get_my_data()
    
    # Render template
    return render_template('my_template.html', data=data)
```

#### 3. Create Template
Create `templates/my_template.html` with your HTML

### Adding Data Fetchers

Add to `utils/data_fetcher.py`:

```python
def get_my_data():
    """Fetch data from Google Sheets."""
    url = os.getenv('MY_DATA_URL')
    data = fetch_json_from_url(url, timeout=10)
    
    if data is None:
        logger.error("Failed to fetch my data")
        return None
    
    return pd.DataFrame(data)
```

### Adding Authentication

Add to `utils/auth_helpers.py`:

```python
def validate_myrole_credentials(username, password):
    """Validate credentials for new role."""
    env_username = os.getenv('MYROLE_USERNAME')
    env_password = os.getenv('MYROLE_PASSWORD')
    
    return username == env_username and password == env_password
```

### Debugging

#### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Session
```python
print(f"Session: {dict(session)}")
print(f"Role: {session.get('role')}")
```

#### Test Data Fetching
```python
from utils.data_fetcher import get_student_data
df = get_student_data()
print(df.head() if df is not None else "Failed")
```

---

## Deployment

### Production Checklist
- [ ] Set strong `FLASK_SECRET_KEY`
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Regular backups of .env file
- [ ] Implement rate limiting
- [ ] Add CSRF protection

### Deploy with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Deploy with Nginx (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Troubleshooting

### Common Issues

#### "Module not found: blueprints"
**Fix**: Make sure you're in project root
```bash
cd c:\Users\LENOVO\Desktop\gitprojects\bcaofficial
python app.py
```

#### "STUDENT_DATA_for_login not configured"
**Fix**: Add to `.env` file
```env
STUDENT_DATA_for_login=https://script.google.com/macros/s/YOUR_ID/exec
```

#### "Student data not available"
**Causes**:
1. Google Script URL incorrect
2. Sheet columns missing/renamed
3. Network connectivity issues

**Fix**:
1. Test URL in browser (should return JSON)
2. Verify sheet has: USN, DOB, Name columns
3. Check internet connection

#### "Invalid USN or Date of Birth"
**Causes**:
1. USN not in database
2. DOB format mismatch
3. Extra spaces in sheet data

**Fix**:
1. Verify USN exists in sheet
2. Try both date formats: YYYY-MM-DD and DD/MM/YYYY
3. Clean up sheet data (trim spaces)

#### "Import could not be resolved: docx"
**Fix**: Reinstall python-docx
```bash
pip install python-docx
```

#### Session/Login Issues
**Fix**: Clear browser cookies and restart Flask app

---

## API Reference

### Public Endpoints
- `GET /` - Landing page
- `GET /login` - Dynamic login page

### Student Endpoints
- `GET /student/login` - Student login page
- `POST /student/login` - Authenticate student
- `GET /student/dashboard` - Student dashboard
- `GET /student/attendance` - Attendance view
- `GET /student/marks` - Internal marks
- `GET /student/profile` - Student profile
- `GET /student/logout` - Logout

### Faculty Endpoints
- `GET /faculty/login` - Faculty login
- `POST /faculty/login` - Authenticate faculty
- `GET /faculty/dashboard` - Faculty dashboard
- `GET /faculty/gfapplications` - GF applications
- `GET /faculty/admission-applications` - Admissions
- `GET /faculty/bills-report` - Teaching records
- `GET /faculty/bills-report/docx` - Download DOCX report
- `GET /faculty/logout` - Logout

### Admin Endpoints
- `GET /admin/login` - Admin login
- `POST /admin/login` - Authenticate admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/gfapplications` - Manage GF apps
- `GET /admin/admission-applications` - Manage admissions
- `GET /admin/documents-tracking` - Document tracking
- `GET /admin/logout` - Logout

### Attender Endpoints
- `GET /attender/login` - Attender login
- `POST /attender/login` - Authenticate attender
- `GET /attender/dashboard` - Attender dashboard
- `GET /attender/documents-tracking` - Document tracking
- `GET /attender/logout` - Logout

---

## Support & Contact

- **Repository**: https://github.com/GitKaran4723/bcaofficial
- **Issues**: Contact department administrator
- **Email**: [BCA Department Email]

---

## License

Proprietary - BCA Department, Bangalore University © 2025

---

**Last Updated**: November 5, 2025  
**Version**: 2.0  
**Maintained by**: BCA Department Faculty
