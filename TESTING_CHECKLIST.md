# Testing & Deployment Checklist

## Pre-Deployment Checklist

### ✅ 1. Environment Setup
- [ ] `.env` file exists and has all required variables
- [ ] `STUDENT_DATA_for_login` is set and points to valid Google Script
- [ ] All Google Script URLs are accessible and return JSON
- [ ] `FLASK_SECRET_KEY` is set to a secure random string
- [ ] Credentials for admin, faculty are set correctly

### ✅ 2. Dependencies
- [ ] `requirements.txt` includes all dependencies (including pandas)
- [ ] Virtual environment is activated
- [ ] All packages installed: `pip install -r requirements.txt`
- [ ] No import errors when running `python app.py`

### ✅ 3. File Structure
```
bcaofficial/
├── app.py ✓
├── app_old.py ✓ (backup)
├── telegram_bot.py ✓
├── requirements.txt ✓
├── .env ✓
├── blueprints/ ✓
│   ├── __init__.py
│   ├── student.py
│   ├── faculty.py
│   ├── admin.py
│   ├── parent.py
│   └── home.py
├── utils/ ✓
│   ├── __init__.py
│   ├── data_fetcher.py
│   └── auth_helpers.py
├── templates/ ✓
│   ├── student_login.html
│   ├── student_dashboard.html
│   ├── student_attendance.html
│   ├── student_marks.html
│   ├── faculty_login.html
│   ├── faculty_dashboard.html
│   ├── login.html
│   ├── dashboard.html
│   ├── admissionApp.html
│   ├── gfApp.html
│   ├── landing.html
│   ├── error.html
│   ├── parent_login.html
│   └── parent_dashboard.html
└── Documentation/ ✓
    ├── README.md
    ├── MIGRATION.md
    ├── QUICKSTART.md
    ├── IMPLEMENTATION_SUMMARY.md
    └── ARCHITECTURE.md
```

## 🧪 Testing Checklist

### Test 1: Application Startup
```powershell
python app.py
```
**Expected Output:**
```
INFO - Starting Flask app in PRODUCTION mode
INFO - All blueprints registered successfully
 * Running on http://0.0.0.0:5000
```
- [ ] No errors on startup
- [ ] Port 5000 is accessible
- [ ] No missing import errors

### Test 2: Public Pages
Visit: `http://localhost:5000`
- [ ] Landing page loads
- [ ] Updates/notices display (or shows placeholder)
- [ ] "Login" button is visible
- [ ] No console errors

### Test 3: Student Login
1. **Navigate**: `http://localhost:5000/student/login`
   - [ ] Login form displays with USN and DOB fields
   - [ ] Date picker works for DOB field

2. **Test Invalid Login**:
   - USN: `INVALID123`
   - DOB: `2000-01-01`
   - [ ] Shows error: "Invalid USN or Date of Birth"

3. **Test Valid Login** (use data from your Google Sheet):
   - USN: `<valid USN from sheet>`
   - DOB: `<matching DOB from sheet>`
   - [ ] Login succeeds
   - [ ] Redirects to `/student/dashboard`
   - [ ] Dashboard shows student name and USN
   - [ ] Session is created (check browser dev tools)

4. **Student Dashboard**:
   - [ ] "My Attendance" card is clickable
   - [ ] "Internal Marks" card is clickable
   - [ ] "Notices" card links to home
   - [ ] "Logout" button visible

5. **Attendance Page**: Click "My Attendance"
   - [ ] Page loads at `/student/attendance`
   - [ ] Shows placeholder message (no data yet)
   - [ ] Navigation works (back to dashboard)

6. **Marks Page**: Click "Internal Marks"
   - [ ] Page loads at `/student/marks`
   - [ ] Shows placeholder message (no data yet)
   - [ ] Navigation works

7. **Logout**:
   - [ ] Click logout
   - [ ] Redirects to landing page
   - [ ] Session is cleared
   - [ ] Cannot access `/student/dashboard` without login

### Test 4: Faculty Login
1. **Navigate**: `http://localhost:5000/faculty/login`
   - [ ] Login form displays

2. **Test Login**:
   - Username: `<TEACHER_USERNAME from .env>`
   - Password: `<TEACHER_PASSWORD from .env>`
   - [ ] Login succeeds
   - [ ] Redirects to `/faculty/dashboard`
   - [ ] Dashboard displays faculty name

3. **View Applications**:
   - [ ] "Faculty Applications" card is clickable
   - [ ] "Admission Applications" card is clickable
   - [ ] Can view GF applications
   - [ ] Can view admission data

4. **Logout**:
   - [ ] Logout button works
   - [ ] Session cleared

### Test 5: Admin Login
1. **Navigate**: `http://localhost:5000/admin/login`
   - [ ] Login form displays

2. **Test Login**:
   - Username: `<LOGIN_USERNAME from .env>`
   - Password: `<LOGIN_PASSWORD from .env>`
   - [ ] Login succeeds
   - [ ] Redirects to `/admin/dashboard`

3. **View Applications**:
   - [ ] "Faculty Applications" link works
   - [ ] "Admission Applications" link works
   - [ ] Data displays correctly with stats

4. **API Endpoint**: Test in browser
   - URL: `http://localhost:5000/admin/api/student/<valid_app_id>`
   - [ ] Returns JSON with student data
   - [ ] Returns 404 for invalid ID
   - [ ] Returns 401 if not logged in

5. **Logout**:
   - [ ] Works correctly

### Test 6: Legacy URLs (Backward Compatibility)
- [ ] `http://localhost:5000/login` → redirects to `/admin/login`
- [ ] `http://localhost:5000/gfapplications` → redirects correctly
- [ ] `http://localhost:5000/admission-applications` → redirects correctly

### Test 7: Error Handling
1. **404 Page**:
   - Visit: `http://localhost:5000/nonexistent`
   - [ ] Shows custom error page
   - [ ] No stack trace visible

2. **Unauthorized Access**:
   - Visit: `http://localhost:5000/student/dashboard` (without login)
   - [ ] Redirects to login
   - [ ] Shows warning message

3. **Google Sheets Unreachable**:
   - Temporarily set invalid URL in `.env`
   - [ ] Shows "Data unavailable" message
   - [ ] Doesn't crash the app
   - [ ] Error logged in console

### Test 8: Session Security
Check browser dev tools (Application → Cookies):
- [ ] Session cookie is `HttpOnly`
- [ ] Session cookie is `SameSite=Lax`
- [ ] Session clears on logout

### Test 9: Telegram Bot (Optional)
If Telegram bot is configured:
- [ ] Webhook endpoint `/telegram` is accessible
- [ ] Bot responds to commands
- [ ] Session handling works

## 📋 Data Validation Checklist

### Google Sheets Structure

#### Sheet: FULL_STUDENTS (for login)
Check your sheet has these columns (case may vary):
- [ ] USN or Seat Number or ID (student identifier)
- [ ] DOB or Date of Birth (authentication field)
- [ ] Name or Candidate Name (display name)
- [ ] Batch (e.g., "24-27")
- [ ] Semester (e.g., "1", "2", etc.)
- [ ] Section (e.g., "A", "B")

**Test Data Row:**
| USN | Name | DOB | Batch | Semester | Section |
|-----|------|-----|-------|----------|---------|
| 1BY22CS001 | Test Student | 2000-01-15 | 24-27 | 3 | A |

#### Sheet: ADMISSION_DATA
- [ ] Has proper structure for admission applications
- [ ] Includes: Application, Candidate Name, Rank, etc.

#### Sheet: GF_APPLICATIONS
- [ ] Returns list of application records
- [ ] Includes photo URLs, CV links, etc.

### Apps Script Endpoints
Test each URL in browser (should return JSON):

1. **Student Data**:
   ```
   <STUDENT_DATA_for_login URL>
   ```
   - [ ] Returns JSON array
   - [ ] Each object has USN, DOB, Name fields

2. **Admission Data**:
   ```
   <ADMISSION_SCRIPT_URL>
   ```
   - [ ] Returns JSON array
   - [ ] Has admission application fields

3. **GF Applications**:
   ```
   <GOOGLE_SCRIPT_URL>
   ```
   - [ ] Returns JSON array
   - [ ] Has faculty application data

4. **Updates**:
   ```
   <UPDATES_JSON_URL>
   ```
   - [ ] Returns JSON with "updates" and "last_updated"

## 🚀 Deployment Checklist

### Production Environment

#### 1. Server Setup
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] `.env` file configured with production values

#### 2. Security Configuration
- [ ] `FLASK_DEBUG=false` in production `.env`
- [ ] Strong `FLASK_SECRET_KEY` (min 32 random characters)
- [ ] HTTPS enabled (SSL certificate)
- [ ] Firewall configured (only necessary ports open)

#### 3. WSGI Server (Gunicorn or uWSGI)
```bash
# Install gunicorn
pip install gunicorn

# Test run
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
- [ ] Gunicorn starts without errors
- [ ] Multiple workers running
- [ ] Application accessible

#### 4. Systemd Service (Linux)
Create `/etc/systemd/system/bcaportal.service`:
```ini
[Unit]
Description=BCA Portal
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/bcaofficial
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```
- [ ] Service file created
- [ ] Service starts: `sudo systemctl start bcaportal`
- [ ] Service enabled: `sudo systemctl enable bcaportal`
- [ ] Service restarts on failure

#### 5. Reverse Proxy (Nginx)
Create `/etc/nginx/sites-available/bcaportal`:
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
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] HTTPS redirect enabled
- [ ] Nginx restarted

#### 6. Monitoring
- [ ] Logging configured (syslog or file)
- [ ] Log rotation set up
- [ ] Uptime monitoring enabled
- [ ] Error alerting configured

#### 7. Backup Strategy
- [ ] Database/session backups (if using Redis/DB)
- [ ] Code repository backup
- [ ] `.env` file backup (secure location)
- [ ] Recovery plan documented

## 🐛 Troubleshooting Guide

### Issue: "Module not found: blueprints"
**Solution:**
```powershell
cd c:\Users\LENOVO\Desktop\gitprojects\bcaofficial
python app.py  # Make sure you're in project root
```

### Issue: "STUDENT_DATA_for_login not configured"
**Solution:**
Add to `.env`:
```env
STUDENT_DATA_for_login=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
```

### Issue: "Invalid USN or Date of Birth"
**Possible Causes:**
1. USN not in Google Sheet → Check sheet
2. DOB format mismatch → Try YYYY-MM-DD
3. Extra spaces in sheet data → Clean data
4. Google Script URL incorrect → Test URL in browser

**Debug:**
Check logs for details:
```powershell
python app.py
# Look for lines starting with "WARNING" or "ERROR"
```

### Issue: "Admission data unavailable"
**Check:**
1. `ADMISSION_SCRIPT_URL` is correct
2. Google Script returns valid JSON
3. Timeout issues (increase timeout in `data_fetcher.py`)

### Issue: Port 5000 already in use
**Solution:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use different port
python app.py --port 5001
```

## ✅ Final Verification

Before going live:
- [ ] All tests in this checklist pass
- [ ] No errors in application logs
- [ ] All user roles can login
- [ ] All pages load correctly
- [ ] Data displays properly
- [ ] Error pages work
- [ ] Sessions work correctly
- [ ] Logout works
- [ ] Security measures in place
- [ ] Backup plan ready
- [ ] Documentation up to date

## 📞 Support Contacts

- **Technical Issues**: Department IT Team
- **Google Sheets**: Spreadsheet Administrator
- **Hosting/Server**: Server Administrator
- **Code Issues**: Development Team

---

**Last Updated**: October 11, 2025  
**Version**: 2.0.0 (Modular Architecture)
