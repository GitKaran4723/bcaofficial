# Quick Start Guide for Developers

## Getting Started in 5 Minutes

### 1. Clone and Setup
```bash
cd c:\Users\LENOVO\Desktop\gitprojects\bcaofficial
pip install -r requirements.txt
```

### 2. Verify Environment Variables
Check your `.env` file has all required variables:
```bash
# On PowerShell
Get-Content .env
```

Required variables:
- `STUDENT_DATA_for_login` (NEW!)
- `FLASK_SECRET_KEY`
- `LOGIN_USERNAME` / `LOGIN_PASSWORD`
- `TEACHER_USERNAME` / `TEACHER_PASSWORD`
- All Google Script URLs

### 3. Run the Application
```bash
python app.py
```

Visit: http://localhost:5000

### 4. Test Student Login
1. Go to http://localhost:5000
2. Click "Login" → Select "Student"
3. Enter:
   - **USN**: (from your STUDENT_DATA_for_login sheet)
   - **DOB**: (matching DOB in the sheet)
4. Should see student dashboard

### 5. Test Admin/Faculty Login
- **Admin**: http://localhost:5000/admin/login
  - Use `LOGIN_USERNAME` / `LOGIN_PASSWORD` from `.env`
- **Faculty**: http://localhost:5000/faculty/login
  - Use `TEACHER_USERNAME` / `TEACHER_PASSWORD` from `.env`

## Project Structure (Quick Reference)

```
app.py                    # Main entry point
├── blueprints/
│   ├── student.py        # Student routes
│   ├── faculty.py        # Faculty routes  
│   ├── admin.py          # Admin routes
│   ├── parent.py         # Parent routes
│   └── home.py           # Public routes
├── utils/
│   ├── data_fetcher.py   # Google Sheets API calls
│   └── auth_helpers.py   # Authentication logic
└── templates/            # HTML files
```

## Common Tasks

### Add a New Route

1. **Choose the right blueprint** (`blueprints/student.py`, etc.)
2. **Add your route function:**
   ```python
   @student_bp.route('/my-new-page')
   def my_new_page():
       if session.get('role') != 'Student':
           return redirect(url_for('student.login'))
       return render_template('my_template.html')
   ```
3. **Create template** in `templates/my_template.html`

### Fetch Data from Google Sheets

1. **Add function to `utils/data_fetcher.py`:**
   ```python
   def get_my_data():
       url = os.getenv('MY_DATA_URL')
       data = fetch_json_from_url(url)
       if data is None:
           return None
       return pd.DataFrame(data)
   ```
2. **Use in your route:**
   ```python
   from utils.data_fetcher import get_my_data
   
   @student_bp.route('/my-data')
   def show_my_data():
       df = get_my_data()
       if df is None:
           return render_template('error.html', message='Data unavailable')
       return render_template('my_data.html', data=df.to_dict('records'))
   ```

### Add Authentication for New Role

1. **Add to `utils/auth_helpers.py`:**
   ```python
   def validate_myrole_credentials(username, password):
       # Your validation logic
       return True  # or False
   ```
2. **Use in blueprint:**
   ```python
   from utils.auth_helpers import validate_myrole_credentials
   
   if validate_myrole_credentials(username, password):
       session['role'] = 'MyRole'
       return redirect(url_for('myrole.dashboard'))
   ```

## Debugging Tips

### Check Logs
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
logger.error("Error message")
logger.exception("Error with stack trace")
```

### Check Session Data
In your route:
```python
print(f"Session: {session}")
print(f"Role: {session.get('role')}")
print(f"USN: {session.get('usn')}")
```

### Test Google Sheets Connection
```python
from utils.data_fetcher import get_student_data
df = get_student_data()
print(df.head() if df is not None else "Failed to fetch")
```

### Check Environment Variables
```python
import os
print(f"Student data URL: {os.getenv('STUDENT_DATA_for_login')}")
```

## File Locations

| What you need | Where to find it |
|---------------|------------------|
| Student routes | `blueprints/student.py` |
| Admin routes | `blueprints/admin.py` |
| Faculty routes | `blueprints/faculty.py` |
| Auth logic | `utils/auth_helpers.py` |
| Data fetching | `utils/data_fetcher.py` |
| Student templates | `templates/student_*.html` |
| Main app config | `app.py` |
| Environment vars | `.env` |
| Dependencies | `requirements.txt` |

## Testing Credentials

### Student Login
- **USN**: Check your `STUDENT_DATA_for_login` sheet
- **DOB**: Must match exactly (format: YYYY-MM-DD or DD/MM/YYYY)

### Admin Login
- **Username**: Value of `LOGIN_USERNAME` in `.env`
- **Password**: Value of `LOGIN_PASSWORD` in `.env`

### Faculty Login
- **Username**: Value of `TEACHER_USERNAME` in `.env`
- **Password**: Value of `TEACHER_PASSWORD` in `.env`

## Common Errors & Fixes

### "Module not found: blueprints"
```bash
# Make sure you're in the project root
cd c:\Users\LENOVO\Desktop\gitprojects\bcaofficial
python app.py
```

### "STUDENT_DATA_for_login not configured"
Add to `.env`:
```env
STUDENT_DATA_for_login=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
```

### "Student data not available"
1. Check if Google Script URL is correct
2. Test the URL in browser (should return JSON)
3. Check sheet has proper columns (USN, DOB, Name)

### "Invalid USN or Date of Birth"
1. Check USN exists in the sheet
2. Verify DOB format matches (try YYYY-MM-DD)
3. Check for extra spaces in sheet data

## Next Steps

1. **Read**: `README.md` for full documentation
2. **Review**: `MIGRATION.md` to understand what changed
3. **Extend**: Add your own routes and features
4. **Test**: Try all login flows and features

## Need Help?

- Check `README.md` for detailed documentation
- Review `MIGRATION.md` for architecture details
- Contact the department administrator

Happy coding! 🚀
