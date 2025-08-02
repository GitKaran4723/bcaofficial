from flask import Blueprint, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

telegram_bp = Blueprint('telegram_bp', __name__)
TOKEN = os.getenv("TELEGRAM_token")
API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
SESSION = {}


@telegram_bp.route('/telegram', methods=['POST'])
def webhook():
    data = request.get_json()
    message = data['message']
    chat_id = message['chat']['id']
    user_input = message.get('text', '').strip()

    # ✅ Restart on /start or /stop
    if user_input.lower() in ["/start", "/stop"]:
        SESSION[chat_id] = {'step': 'batch'}
        return send_message(chat_id, "Enter Batch (e.g., 24-27):")

    # ✅ Initialize session if not exists
    if chat_id not in SESSION:
        SESSION[chat_id] = {'step': 'batch'}
        return send_message(chat_id, "Enter Batch (e.g., 24-27):")

    user_session = SESSION[chat_id]
    step = user_session['step']

    # ✅ Step-wise flow
    if step == 'batch':
        user_session['batch'] = user_input
        user_session['step'] = 'semester'
        return send_message(chat_id, "Enter Semester (e.g., 3):")

    elif step == 'semester':
        user_session['semester'] = user_input
        user_session['step'] = 'section'
        return send_message(chat_id, "Enter Section (e.g., A):")

    elif step == 'section':
        user_session['section'] = user_input.upper()
        user_session['step'] = 'subject'
        return send_message(chat_id, "Enter Subject (e.g., PS):")

    elif step == 'subject':
        user_session['subject'] = user_input.upper()
        user_session['step'] = 'fetching_data'
        return fetch_and_store_attendance(chat_id, user_session)

    elif step == 'name':
        user_session['name'] = user_input.upper()
        user_session['step'] = 'usn'
        return send_message(chat_id, "Enter Your USN:")

    elif step == 'usn':
        user_session['usn'] = user_input.upper()
        user_session['step'] = 'done'
        send_message(chat_id, "⏳ Preparing your attendance report...")
        return show_attendance(chat_id, user_session)

    else:
        # Reset if user sends something unexpected
        SESSION[chat_id] = {'step': 'batch'}
        return send_message(chat_id, "Session reset. Enter Batch (e.g., 24-27):")

# ✅ Send message to Telegram


def send_message(chat_id, text):
    requests.post(API_URL, json={'chat_id': chat_id, 'text': text})
    return 'ok'

# ✅ Fetch data from Google Sheet and store in session


def fetch_and_store_attendance(chat_id, session):
    sheet_url = os.getenv("ATTENDANCE_Script")

    params = {
        "batch": session['batch'],
        "semester": session['semester'],
        "section": session['section'],
        "subject": session['subject']
    }

    response = requests.get(sheet_url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            session['attendance_data'] = data
            session['step'] = 'name'
            return send_message(chat_id, "Enter Your Name:")
        except Exception as e:
            session['step'] = 'batch'
            return send_message(chat_id, "⚠️ Failed to parse data. Start again with /start")
    else:
        session['step'] = 'batch'
        return send_message(chat_id, "⚠️ Unable to fetch data. Start again with /start")

# ✅ Show attendance for given name and usn


def show_attendance(chat_id, session):
    data = session.get('attendance_data')
    if not data:
        return send_message(chat_id, "⚠️ Attendance data not found. Please /start again.")

    usn = session['usn']
    name_input = session['name']
    subject = session['subject']
    headers = data[0]
    date_columns = headers[3:]

    for row in data[1:]:
        if row[0].upper() == usn and row[1].upper() == name_input:
            name = row[1]
            percentage = row[2]
            attendance = row[3:]
            absents = [date for date, status in zip(
                date_columns, attendance) if status == 'A']

            message = (
                f"✅ Attendance Details:\n"
                f"Name       : {name}\n"
                f"USN        : {usn}\n"
                f"Subject    : {subject}\n"
                f"Attendance : {percentage}\n"
                f"Absent on  :\n" +
                ("\n".join([f" - {d[:10]}" for d in absents])
                 if absents else " - None")
            )
            return send_message(chat_id, message)

    return send_message(chat_id, "❌ Name or USN not found in the records.")
