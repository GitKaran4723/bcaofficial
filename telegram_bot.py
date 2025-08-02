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
    chat_id = data['message']['chat']['id']
    user_input = data['message'].get('text', '').strip()

    # Step 1: Create session if not exists
    if chat_id not in SESSION:
        SESSION[chat_id] = {'step': 'batch'}

    user_session = SESSION[chat_id]

    # Step 2: Handle steps
    step = user_session['step']

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
        user_session['step'] = 'name'
        return send_message(chat_id, "Enter Your Name:")

    elif step == 'name':
        user_session['name'] = user_input.upper()
        user_session['step'] = 'usn'
        return send_message(chat_id, "Enter Your USN:")

    elif step == 'usn':
        user_session['usn'] = user_input.upper()
        send_message(chat_id, "⏳ Preparing your attendance report...")
        return fetch_attendance(chat_id, user_session)

    else:
        return send_message(chat_id, "Please start again. Send /start to begin.")

# ⬇️ Helper: Send message to Telegram


def send_message(chat_id, text):
    requests.post(API_URL, json={'chat_id': chat_id, 'text': text})
    return 'ok'

# ⬇️ Helper: Fetch attendance data


def fetch_attendance(chat_id, session):
    url = os.getenv("ATTENDANCE_Script")
    url = "https://script.google.com/macros/s/AKfycbxg9qy4Z9Idiio4hnaroXR5hdedM_roLxbLTEQhZcXaPJfIiuh66ucpA0jG0FJuRKuU/exec"
    params = {
        "batch": session['batch'],
        "semester": session['semester'],
        "section": session['section'],
        "subject": session['subject']
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        usn = session['usn']
        name_input = session['name']
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
                    f"Attendance : {percentage}\n"
                    f"Absent on  :\n" +
                    "\n".join([f" - {d[:10]}" for d in absents]
                              ) if absents else " - None"
                )
                return send_message(chat_id, message)

        return send_message(chat_id, "❌ Name or USN not found in the records.")

    return send_message(chat_id, "⚠️ Failed to fetch data. Please try again later.")
