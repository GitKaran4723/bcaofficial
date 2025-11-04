# Migration Guide: Monolithic to Modular Architecture

## Overview
The BCA Portal has been restructured from a single-file monolithic application to a modular, maintainable architecture using Flask Blueprints.

## What Changed

### 1. Project Structure

**Before:**
```
bcaofficial/
├── app.py (650+ lines, all routes mixed)
├── telegram_bot.py
├── requirements.txt
└── templates/
```

**After:**
```
bcaofficial/
├── app.py (main, 120 lines)
├── app_old.py (backup of original)
├── blueprints/
│   ├── __init__.py
│   ├── student.py      # Student-specific routes
│   ├── faculty.py      # Faculty routes
│   ├── admin.py        # Admin routes
│   ├── parent.py       # Parent routes (placeholder)
│   └── home.py         # Public pages
├── utils/
│   ├── __init__.py
│   ├── data_fetcher.py # Google Sheets integration
│   └── auth_helpers.py # Authentication logic
├── telegram_bot.py
├── requirements.txt (added pandas)
└── templates/
    ├── student_login.html (updated for USN + DOB)
    ├── student_dashboard.html (enhanced)
    ├── student_attendance.html (NEW)
    ├── student_marks.html (NEW)
    └── ... (other templates)
```

### 2. Key Improvements

#### Authentication
- **Student Login**: Now uses USN + Date of Birth (not username/password)
  - Validates against `STUDENT_DATA_for_login` Google Sheet
  - Supports multiple date formats (YYYY-MM-DD, DD/MM/YYYY, etc.)
  - Stores student info in session

#### Code Organization
- **Blueprints**: Each user role has its own module
  - `student.py`: Student login, dashboard, attendance, marks
  - `faculty.py`: Faculty login, dashboard, view applications
  - `admin.py`: Admin login, manage applications, API endpoints
  - `parent.py`: Parent login (placeholder for future)
  - `home.py`: Public landing page

- **Utilities**: Shared functions extracted
  - `data_fetcher.py`: All Google Sheets data fetching
  - `auth_helpers.py`: All authentication validation

#### Error Handling
- Consistent error handling across all data fetchers
- Returns `None` on failure (not mixed return types)
- Proper logging with Python's logging module
- Graceful fallbacks for external API failures

#### Security Enhancements
- Environment variable validation on startup
- Session cookies configured as HTTP-only
- Debug mode from environment variable
- Role-based access control on all routes

### 3. URL Changes

#### Student Routes (NEW)
| Old URL | New URL | Notes |
|---------|---------|-------|
| `/student/login` | `/student/login` | Now uses USN + DOB |
| `/student/dashboard` | `/student/dashboard` | Enhanced with cards |
| N/A | `/student/attendance` | NEW: View attendance |
| N/A | `/student/marks` | NEW: View internal marks |

#### Admin Routes
| Old URL | New URL | Notes |
|---------|---------|-------|
| `/login` | `/admin/login` | Admin-specific |
| `/admin` | `/admin/dashboard` | Unchanged |
| `/gfapplications` | `/admin/gfapplications` | Moved to admin |
| `/admission-applications` | `/admin/admission-applications` | Moved |

#### Faculty Routes
| Old URL | New URL | Notes |
|---------|---------|-------|
| `/faculty/login` | `/faculty/login` | Unchanged |
| `/faculty/dashboard` | `/faculty/dashboard` | Unchanged |
| N/A | `/faculty/gfapplications` | NEW: Faculty can view |
| N/A | `/faculty/admission-applications` | NEW: Faculty access |

#### Legacy Redirects
For backward compatibility, old URLs redirect to new locations:
- `/login` → `/admin/login`
- `/gfapplications` → `/admin/gfapplications`
- `/admission-applications` → `/admin/admission-applications`

### 4. Environment Variables

#### New Required Variables
```env
STUDENT_DATA_for_login=https://script.google.com/macros/s/.../exec
```

#### All Required Variables
```env
FLASK_SECRET_KEY=your-secret-key
FLASK_DEBUG=false
LOGIN_USERNAME=admin
LOGIN_PASSWORD=admin123
TEACHER_USERNAME=karan
TEACHER_PASSWORD=karan135
ADMISSION_SCRIPT_URL=https://...
GOOGLE_SCRIPT_URL=https://...
UPDATES_JSON_URL=https://...
STUDENT_DATA_for_login=https://...
TELEGRAM_token=...
ATTENDANCE_Script=https://...
```

### 5. Google Sheets Requirements

#### Student Login Sheet (FULL_STUDENTS)
Required columns:
- `USN` or `Seat Number` or `ID` (student identifier)
- `DOB` or `Date of Birth` (for authentication)
- `Name` or `Candidate Name`
- Other profile fields (Batch, Semester, Section, etc.)

**Format Notes:**
- USN: Case-insensitive, whitespace is stripped
- DOB: Supports YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, etc.

#### Attendance Sheet
Parameters: `batch`, `semester`, `section`, `subject`
Returns: 2D array with headers + attendance records

#### Marks Sheet (Future)
Will contain: USN, Subject, IA1, IA2, IA3, Total

### 6. Migration Steps for Deployment

1. **Backup Current Deployment**
   ```bash
   cp app.py app_backup_$(date +%Y%m%d).py
   ```

2. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

3. **Install New Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Update Environment Variables**
   - Add `STUDENT_DATA_for_login` to `.env`
   - Verify all other variables are set

5. **Test Locally**
   ```bash
   python app.py
   ```
   Visit http://localhost:5000 and test:
   - Student login with valid USN + DOB
   - Faculty login
   - Admin login
   - Public landing page

6. **Restart Production Server**
   ```bash
   # If using systemd
   sudo systemctl restart bcaportal
   
   # If using gunicorn
   pkill gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### 7. Testing Checklist

#### Student Portal
- [ ] Login with USN + DOB works
- [ ] Invalid credentials show error
- [ ] Dashboard loads with student name
- [ ] Attendance page accessible (shows placeholder)
- [ ] Marks page accessible (shows placeholder)
- [ ] Logout clears session

#### Faculty Portal
- [ ] Login with faculty credentials
- [ ] Dashboard loads
- [ ] Can view GF applications
- [ ] Can view admission data

#### Admin Portal
- [ ] Login with admin credentials
- [ ] Dashboard loads
- [ ] GF applications display
- [ ] Admission applications with stats display
- [ ] API endpoint `/admin/api/student/<id>` works

#### Legacy URLs
- [ ] `/login` redirects to `/admin/login`
- [ ] `/gfapplications` redirects properly
- [ ] `/admission-applications` redirects properly

### 8. Known Issues & TODOs

#### Completed ✅
- [x] Added pandas to requirements.txt
- [x] Fixed `get_admission_dataframe` return type consistency
- [x] Created missing student/parent templates
- [x] Implemented student USN + DOB authentication
- [x] Separated routes into blueprints
- [x] Created data fetcher utilities
- [x] Enhanced error handling and logging

#### Pending ⚠️
- [ ] Implement actual attendance data fetching (currently placeholder)
- [ ] Implement actual marks data fetching (currently placeholder)
- [ ] Parent authentication logic
- [ ] Link parents to students
- [ ] Add unit tests
- [ ] Implement password hashing
- [ ] Add CSRF protection
- [ ] Rate limiting on login endpoints
- [ ] Redis/database for Telegram bot sessions

### 9. Rollback Plan

If issues arise, rollback to the old version:

```bash
# Stop the server
pkill -f "python app.py"

# Restore old app.py
cp app_old.py app.py

# Restart
python app.py
```

### 10. Support & Documentation

- **Architecture Diagram**: See `README.md`
- **API Documentation**: See `README.md` (API Endpoints section)
- **Environment Setup**: See `README.md` (Setup Instructions)

### 11. Performance Notes

- Data fetching functions have 6-second timeouts
- Google Sheets endpoints should respond in < 2 seconds
- Session data stored server-side (in-memory by default)
- Consider Redis for production session storage

### 12. Next Phase Priorities

1. **Student Attendance Integration**
   - Create attendance Google Sheet with proper structure
   - Implement `get_student_attendance()` in `data_fetcher.py`
   - Update `student.attendance()` route to fetch real data

2. **Student Marks Integration**
   - Create marks Google Sheet
   - Implement `get_student_marks()` in `data_fetcher.py`
   - Update `student.marks()` route

3. **Parent Portal**
   - Design parent-student linking mechanism
   - Create parent authentication
   - Build parent dashboard with child's progress

## Questions?

Contact the development team or check the comprehensive `README.md` file.
