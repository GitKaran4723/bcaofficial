from flask import Blueprint, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

telegram_bp = Blueprint('telegram_bp', __name__)
TOKEN = os.getenv("TELEGRAM_token")
API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
SESSION = {}

SUBJECTS = {
    "1": [("DS", "Discrete Structures"), ("PST", "Problem Solving Technique"), ("CA", "Computer Architecture")],
    "3": [("PS", "Probability & Statistics"), ("AI", "Artificial Intelligence"), ("DBMS", "Database Systems")],
    "5": [("ML", "Machine Learning"), ("WT", "Web Technologies")],
}

SECTIONS = {
    "24-27": ["A", "B"],
    "25-28": ["A", "B", "C"]
}

@telegram_bp.route('/telegram', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'callback_query' in data:
        callback = data['callback_query']
        chat_id = callback['message']['chat']['id']
        query_data = callback['data']
        user_session = SESSION.get(chat_id, {})

        if query_data.startswith("batch:"):
            batch = query_data.split(":")[1]
            user_session['batch'] = batch
            user_session['step'] = 'semester'
            SESSION[chat_id] = user_session
            return send_keyboard(chat_id, "📘 Select Semester:", [str(i) for i in range(1, 7)], prefix="semester")

        elif query_data.startswith("semester:"):
            semester = query_data.split(":")[1]
            user_session['semester'] = semester
            user_session['step'] = 'section'
            SESSION[chat_id] = user_session
            sections = SECTIONS.get(user_session['batch'], [])
            return send_keyboard(chat_id, "🏷️ Select Section:", sections, prefix="section")

        elif query_data.startswith("section:"):
            section = query_data.split(":")[1]
            user_session['section'] = section
            user_session['step'] = 'subject'
            SESSION[chat_id] = user_session
            subjects = SUBJECTS.get(user_session['semester'])
            if not subjects:
                return send_message(chat_id, "Coming Soon 😎 Please stay cool.")
            return send_keyboard(chat_id, f"📚 Select Subject:",
                                 [f"{code} - {label}" for code, label in subjects], prefix="subject")

        elif query_data.startswith("subject:"):
            subject_code = query_data.split(":")[1]
            user_session['subject'] = subject_code
            user_session['step'] = 'name'
            SESSION[chat_id] = user_session
            return send_message(chat_id, "👤 Enter Your Name:")

        elif query_data == "new_student":
            SESSION[chat_id] = {'step': 'batch'}
            return send_keyboard(chat_id, "🔰 Select Batch:", ["24-27", "25-28"], prefix="batch")

        elif query_data == "other_subject":
            user_session['step'] = 'subject'
            SESSION[chat_id] = user_session
            semester = user_session.get('semester')
            subjects = SUBJECTS.get(semester)
            if not subjects:
                return send_message(chat_id, "Coming Soon 😎 Please stay cool.")
            return send_keyboard(chat_id, f"📚 Select Another Subject:",
                                 [f"{code} - {label}" for code, label in subjects], prefix="subject")

        elif query_data == "exit":
            SESSION.pop(chat_id, None)
            return send_message(chat_id, "👋 Session ended. Type /start to begin again.")

        return 'ok'

    message = data['message']
    chat_id = message['chat']['id']
    user_input = message.get('text', '').strip()
    user_session = SESSION.get(chat_id, {})

    if user_input.lower() in ["/start", "/stop"]:
        SESSION[chat_id] = {'step': 'batch'}
        return send_keyboard(chat_id, "🔰 Select Batch:", ["24-27", "25-28"], prefix="batch")

    step = user_session.get('step')

    if step == 'name':
        user_session['name'] = user_input.upper()
        user_session['step'] = 'usn'
        return send_message(chat_id, "🔑 Enter Your USN:")

    elif step == 'usn':
        user_session['usn'] = user_input.upper()
        return fetch_and_show_attendance(chat_id, user_session)

    else:
        SESSION[chat_id] = {'step': 'batch'}
        return send_keyboard(chat_id, "🔰 Let's start fresh. Select Batch:", ["24-27", "25-28"], prefix="batch")

# --- Helper Functions ---

def send_message(chat_id, text):
    requests.post(API_URL, json={'chat_id': chat_id, 'text': text})
    return 'ok'

def send_keyboard(chat_id, text, options, prefix=""):
    buttons = [[{"text": opt, "callback_data": f"{prefix}:{opt.split(' - ')[0]}"}] for opt in options]
    buttons.append([{"text": "❌ Exit", "callback_data": "exit"}])
    payload = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': {'inline_keyboard': buttons}
    }
    requests.post(API_URL, json=payload)
    return 'ok'

def fetch_and_show_attendance(chat_id, session):
    sheet_url = os.getenv("ATTENDANCE_Script")
    params = {
        "batch": session['batch'],
        "semester": session['semester'],
        "section": session['section'],
        "subject": session['subject']
    }

    response = requests.get(sheet_url, params=params)
    if response.status_code != 200:
        return send_message(chat_id, "⚠️ Unable to fetch data. Try again later.")

    try:
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Invalid format")

        session['attendance_data'] = data
        usn = session['usn']
        name_input = session['name']
        headers = data[0]
        date_columns = headers[3:]

        for row in data[1:]:
            if row[0].upper() == usn and row[1].upper() == name_input:
                name = row[1]
                percentage = row[2]
                attendance = row[3:]
                absents = [date for date, status in zip(date_columns, attendance) if status == 'A']
                message = (
                    f"✅ Attendance Details:\n"
                    f"Name       : {name}\n"
                    f"USN        : {usn}\n"
                    f"Subject    : {session['subject']}\n"
                    f"Section    : {session['section']}\n"
                    f"Attendance : {percentage}\n"
                    f"Absent on  :\n" +
                    ("\n".join([f" - {d[:10]}" for d in absents]) if absents else " - Superb 👌 You are Very Regular 🤩")
                )
                send_message(chat_id, message)
                return send_keyboard(chat_id, "What would you like to do next?", ["🔁 See Another Subject", "👤 New Student"], prefix="other")

        return send_message(chat_id, "❌ Name or USN not found in records.")
    except:
        return send_message(chat_id, "Coming Soon 😎 Please stay cool.")
