from flask import Blueprint, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

telegram_bp = Blueprint('telegram_bp', __name__)
TOKEN = os.getenv("TELEGRAM_token")
API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

@telegram_bp.route('/telegram', methods=['POST'])
def webhook():
    data = request.get_json()
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text', '')
    requests.post(API_URL, json={'chat_id': chat_id, 'text': f"You said: {text}"})
    return 'ok'
