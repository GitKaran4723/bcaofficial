# Student Profile Feature Documentation

## Overview
Implemented a comprehensive student profile page that displays all student information from the Google Sheets database. The profile automatically shows "Data to be updated" for any missing or unavailable fields.

## Implementation Date
October 11, 2025

## Features Implemented

### 1. Profile Route
**Location**: `blueprints/student.py`

Added new route:
```python
@student_bp.route('/profile')
def profile():
    """View student profile with all details from Google Sheets."""
```

- **Authentication**: Checks if user is logged in as a student
- **Data Source**: Retrieves student information from session (populated during login from Google Sheets)
- **Access**: Available at `/student/profile`

### 2. Profile Template
**Location**: `templates/student_profile.html`

#### Sections:

1. **Profile Overview Card**
   - Student name
   - USN
   - Course
   - Profile avatar icon

2. **Personal Information**
   - Full Name
   - USN (University Seat Number)
   - Date of Birth
   - Gender
   - Mobile Number
   - Email Address
   - Father's Name
   - Mother's Name

3. **Academic Information**
   - Course
   - Batch
   - Current Semester
   - Section
   - Roll Number
   - Admission Date

4. **Address Information**
   - Current Address
   - Permanent Address
   - City
   - State
   - PIN Code

5. **Additional Information**
   - Blood Group
   - Category
   - Religion
   - Nationality
   - Aadhar Number (masked - shows only first 4 digits)

### 3. Dashboard Integration
**Updated**: `templates/student_dashboard.html`

Changed profile card link from:
```html
<a href="#">
```

To:
```html
<a href="{{ url_for('student.profile') }}">
```

## Data Handling

### Available Data Display
When data is present in the Google Sheets, it displays the actual value:
```jinja2
{{ student_info.get('Name', 'Default') }}
```

### Missing Data Display
When data is not available, displays styled message:
```jinja2
{{ student_info.get('Mobile', '<span class="text-orange-600 italic">Data to be updated</span>') | safe }}
```

### Multiple Field Names Support
Checks multiple possible field names from the sheet:
```jinja2
{{ student_info.get('Email', student_info.get('Email ID', 'Data to be updated')) }}
```

### Privacy Protection
Sensitive data like Aadhar numbers are partially masked:
```jinja2
{% if student_info.get('Aadhar') %}
  {{ student_info.get('Aadhar')[:4] }}********
{% else %}
  <span class="text-orange-600 italic">Data to be updated</span>
{% endif %}
```

## Google Sheets Column Mapping

The profile template looks for these column names in the student data sheet:

### Basic Info
- `Name` or `Candidate Name`
- `USN`
- `DOB` or `Date of Birth`
- `Gender`

### Contact
- `Mobile` or `Phone` or `Contact`
- `Email` or `Email ID`

### Family
- `Father's Name` or `Father Name`
- `Mother's Name` or `Mother Name`

### Academic
- `Course` or `Program`
- `Batch` or `Year`
- `Semester` or `Sem`
- `Section`
- `Roll No` or `Roll Number`
- `Admission Date` or `Date of Admission`

### Address
- `Address` or `Current Address`
- `Permanent Address`
- `City`
- `State`
- `PIN Code` or `Pincode`

### Additional
- `Blood Group`
- `Category`
- `Religion`
- `Nationality`
- `Aadhar` or `Aadhar Number`

## User Experience

### Visual Design
- **Modern UI**: Uses Tailwind CSS for responsive, modern design
- **Card Layout**: Information organized in clean cards with gray backgrounds
- **Color Coding**: 
  - Missing data: Orange italic text
  - Section headers: Bold with border
  - Cards: White background with shadows

### Navigation
- **Header**: Shows student name and USN
- **Back Button**: Returns to student dashboard
- **Logout Button**: Direct logout option

### Information Notice
At the bottom of the profile:
> **Note:** If any information is missing or incorrect, please contact the department office or your class coordinator to update your details in the system.

## Security Features

1. **Session Validation**: Checks if user is logged in before showing profile
2. **Data Sanitization**: Uses Jinja2's `| safe` filter only for controlled HTML
3. **Privacy**: Masks sensitive information (Aadhar numbers)
4. **No Direct Database Access**: Uses session data populated during authentication

## Testing Checklist

- [ ] Login with valid student credentials
- [ ] Click "My Profile" from dashboard
- [ ] Verify all available fields display correctly
- [ ] Confirm missing fields show "Data to be updated"
- [ ] Check mobile responsive layout
- [ ] Test "Back to Dashboard" button
- [ ] Test "Logout" button
- [ ] Verify Aadhar number masking (if present)
- [ ] Test with student having incomplete data
- [ ] Test with student having complete data

## Future Enhancements

1. **Edit Functionality**: Allow students to update certain fields
2. **Profile Photo Upload**: Let students upload their photo
3. **Document Uploads**: Allow uploading certificates, ID proof
4. **Verification Status**: Show which fields are verified
5. **Change Requests**: Let students request data changes
6. **Parent Information**: Add parent contact details section
7. **Emergency Contact**: Add emergency contact section
8. **Previous Education**: Show 10th, 12th marks/school details

## API Requirements

### Google Sheets Structure
The `STUDENT_DATA_for_login` sheet should contain these columns for optimal display:

**Required Columns:**
- USN
- DOB
- Name

**Recommended Columns:**
- Gender
- Mobile
- Email
- Father's Name
- Mother's Name
- Course
- Batch
- Semester
- Section
- Address
- City
- State
- Blood Group

**Optional Columns:**
- Roll No
- Admission Date
- Permanent Address
- PIN Code
- Category
- Religion
- Nationality
- Aadhar

## File Changes Summary

### Modified Files:
1. `blueprints/student.py` - Added profile route
2. `templates/student_dashboard.html` - Updated profile card link

### New Files:
1. `templates/student_profile.html` - Complete profile page

## Access Control

**Required Session Data:**
- `session['role']` must be 'Student'
- `session['student_info']` contains all student data
- `session['usn']` contains student USN
- `session['student_name']` contains student name

**Redirect Behavior:**
- If not logged in → Redirect to `/student/login`
- After logout → Redirect to landing page

## Example Usage

1. Student logs in with USN and DOB
2. Clicks "My Profile" from dashboard
3. Views complete profile with all available information
4. Sees "Data to be updated" for missing fields
5. Can navigate back to dashboard or logout

## Support Information

For data updates or corrections, students are instructed to contact:
- Department office
- Class coordinator

This ensures data integrity and proper verification of information changes.
