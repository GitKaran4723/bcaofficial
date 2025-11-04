# BCA Portal Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         BCA Portal                               │
│                      (Flask Application)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├─── app.py (Main Entry Point)
                              │    • Initialize Flask
                              │    • Load Environment Variables
                              │    • Register Blueprints
                              │    • Configure Session Security
                              │    • Error Handlers
                              │
        ┌─────────────────────┴────────────────────────┐
        │                                              │
        ▼                                              ▼
┌──────────────┐                              ┌──────────────┐
│  Blueprints  │                              │   Utilities  │
└──────────────┘                              └──────────────┘
        │                                              │
        ├─── home.py                                  ├─── data_fetcher.py
        │    • Landing Page                           │    • fetch_json_from_url()
        │    • About                                  │    • get_student_data()
        │    • Contact                                │    • get_admission_data()
        │                                             │    • get_gf_applications()
        ├─── student.py                               │    • get_updates()
        │    • Login (USN + DOB)                      │    • get_attendance_data()
        │    • Dashboard                              │
        │    • Attendance View                        ├─── auth_helpers.py
        │    • Marks View                             │    • validate_admin_credentials()
        │    • Logout                                 │    • validate_faculty_credentials()
        │                                             │    • validate_student_credentials()
        ├─── faculty.py                               │    • validate_parent_credentials()
        │    • Login                                  │    • validate_dob_match()
        │    • Dashboard                              │    • parse_date_string()
        │    • View GF Applications                   │
        │    • View Admission Data                    └────────────────┐
        │    • Logout                                                  │
        │                                                               │
        ├─── admin.py                                                  │
        │    • Login                                                   │
        │    • Dashboard                                               │
        │    • Manage GF Applications                                  │
        │    • Manage Admission Data                                   │
        │    • API Endpoints                                           │
        │    • Logout                                                  │
        │                                                               │
        ├─── parent.py (Placeholder)                                   │
        │    • Login                                                   │
        │    • Dashboard                                               │
        │    • Logout                                                  │
        │                                                               │
        └─── telegram_bot.py (Webhook)                                 │
             • Attendance Bot                                          │
             • Interactive Sessions                                    │
                                                                       │
                              ┌────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     External Data Sources                        │
└─────────────────────────────────────────────────────────────────┘
        │
        ├─── Google Sheets (via Apps Script)
        │    • FULL_STUDENTS (Login Data)
        │    • ADMISSION_DATA (Applications)
        │    • GF_APPLICATIONS (Faculty Applications)
        │    • ATTENDANCE (Attendance Records)
        │    • MARKS (Internal Assessments)
        │
        ├─── GitHub JSON
        │    • Updates/Notices Feed
        │
        └─── Telegram API
             • Bot Webhook Endpoint
```

## Request Flow Diagrams

### Student Login Flow

```
┌─────────┐          ┌──────────────┐          ┌───────────────┐
│ Student │          │   Flask App  │          │ Google Sheets │
└────┬────┘          └──────┬───────┘          └───────┬───────┘
     │                      │                          │
     │  GET /student/login  │                          │
     │─────────────────────>│                          │
     │                      │                          │
     │  Render Login Form   │                          │
     │<─────────────────────│                          │
     │                      │                          │
     │  POST (USN, DOB)     │                          │
     │─────────────────────>│                          │
     │                      │                          │
     │                      │  Fetch Student Data      │
     │                      │─────────────────────────>│
     │                      │                          │
     │                      │  Return JSON (Students)  │
     │                      │<─────────────────────────│
     │                      │                          │
     │                      │  Validate USN + DOB      │
     │                      │  (auth_helpers.py)       │
     │                      │                          │
     │  Set Session & Redirect                         │
     │  to Dashboard        │                          │
     │<─────────────────────│                          │
     │                      │                          │
```

### Data Fetching Flow

```
┌──────────┐          ┌───────────────┐          ┌───────────────┐
│ Blueprint│          │ Data Fetcher  │          │ Google Sheets │
└────┬─────┘          └───────┬───────┘          └───────┬───────┘
     │                        │                          │
     │  get_student_data()    │                          │
     │───────────────────────>│                          │
     │                        │                          │
     │                        │  HTTP GET with timeout   │
     │                        │─────────────────────────>│
     │                        │                          │
     │                        │  JSON Response           │
     │                        │<─────────────────────────│
     │                        │                          │
     │                        │  Convert to DataFrame    │
     │                        │  Normalize column names  │
     │                        │                          │
     │  Return DataFrame      │                          │
     │  or None on error      │                          │
     │<───────────────────────│                          │
     │                        │                          │
     │  Check if None         │                          │
     │  Handle gracefully     │                          │
     │                        │                          │
```

## Module Dependencies

```
app.py
  ├── blueprints/
  │   ├── home.py
  │   │   └── utils.data_fetcher (get_updates)
  │   │
  │   ├── student.py
  │   │   ├── utils.auth_helpers (validate_student_credentials)
  │   │   └── utils.data_fetcher (future: attendance, marks)
  │   │
  │   ├── faculty.py
  │   │   ├── utils.auth_helpers (validate_faculty_credentials)
  │   │   └── utils.data_fetcher (get_gf_applications, get_admission_data)
  │   │
  │   ├── admin.py
  │   │   ├── utils.auth_helpers (validate_admin_credentials)
  │   │   └── utils.data_fetcher (get_admission_data, get_gf_applications)
  │   │
  │   ├── parent.py
  │   │   └── utils.auth_helpers (validate_parent_credentials)
  │   │
  │   └── telegram_bot.py (imported as-is)
  │
  └── utils/
      ├── data_fetcher.py
      │   └── requests, pandas, os, logging
      │
      └── auth_helpers.py
          ├── utils.data_fetcher (get_student_data)
          └── pandas, datetime, logging
```

## Session Management

```
┌─────────────────────────────────────────────┐
│            Flask Session                    │
│  (Server-side, HTTP-only, SameSite=Lax)    │
└─────────────────────────────────────────────┘
                  │
                  ├─ role: 'Student' | 'Faculty' | 'Admin' | 'Parent'
                  ├─ logged_in: True | False
                  ├─ username: str (for faculty/admin)
                  │
                  └─ For Students:
                     ├─ usn: str
                     ├─ student_name: str
                     └─ student_info: dict (full profile data)
```

## Template Hierarchy

```
templates/
│
├── Public Pages
│   ├── landing.html (home page with updates)
│   ├── error.html (error display page)
│   ├── about.html (future)
│   └── contact.html (future)
│
├── Student Pages
│   ├── student_login.html (USN + DOB form)
│   ├── student_dashboard.html (quick access cards)
│   ├── student_attendance.html (attendance view)
│   └── student_marks.html (internal marks view)
│
├── Faculty Pages
│   ├── faculty_login.html (username + password)
│   ├── faculty_dashboard.html (faculty tools)
│   └── (shares gfApp.html, admissionApp.html with admin)
│
├── Admin Pages
│   ├── login.html (admin login)
│   ├── dashboard.html (admin dashboard)
│   ├── gfApp.html (guest faculty applications)
│   └── admissionApp.html (admission applications)
│
└── Parent Pages (Placeholder)
    ├── parent_login.html (identifier + password)
    └── parent_dashboard.html (children's progress)
```

## URL Routing Structure

```
/ (home_bp)
├── GET /                    → landing page

/student (student_bp)
├── GET/POST /login          → student login
├── GET /dashboard           → student dashboard
├── GET /attendance          → view attendance
├── GET /marks               → view marks
└── GET /logout              → logout

/faculty (faculty_bp)
├── GET/POST /login          → faculty login
├── GET /dashboard           → faculty dashboard
├── GET /gfapplications      → view GF apps
├── GET /admission-applications → view admissions
└── GET /logout              → logout

/admin (admin_bp)
├── GET/POST /login          → admin login
├── GET /dashboard           → admin dashboard
├── GET /gfapplications      → manage GF apps
├── GET /admission-applications → manage admissions
├── GET /api/student/<id>    → get student JSON
└── GET /logout              → logout

/parent (parent_bp)
├── GET/POST /login          → parent login
├── GET /dashboard           → parent dashboard
└── GET /logout              → logout

/telegram (telegram_bp)
└── POST /                   → telegram webhook

Legacy Redirects (root level)
├── /login                   → /admin/login
├── /gfapplications          → /admin/gfapplications
└── /admission-applications  → /admin/admission-applications
```

## Data Flow Summary

```
User Request
     │
     ▼
 Flask App (app.py)
     │
     ├─ Route matched to Blueprint
     │
     ▼
 Blueprint Route Handler
     │
     ├─ Check session/authentication
     │
     ├─ Call utility function (if needed)
     │   │
     │   ▼
     │  Data Fetcher → Google Sheets API
     │   │
     │   └─ Return DataFrame or None
     │
     ├─ Process data
     │
     ▼
 Render Template
     │
     ▼
HTML Response to User
```

## Security Layers

```
┌─────────────────────────────────────────────┐
│         External Request (HTTPS)            │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│    Session Cookie Validation                │
│    (HTTP-only, SameSite, Secure)            │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│    Role-Based Access Control                │
│    (Check session['role'])                  │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│    Input Validation                         │
│    (Strip, uppercase, sanitize)             │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│    Business Logic                           │
│    (Authentication, data fetching)          │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│    Error Handling & Logging                 │
│    (Try-except, logger)                     │
└─────────────────────────────────────────────┘
```

This modular architecture provides clear separation of concerns, making the application easier to maintain, test, and extend.
