import os
from flask import Flask, render_template
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GOOGLE_SCRIPT_URL = os.getenv('GOOGLE_SCRIPT_URL')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/gfapplications')
def display_data():
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        data = response.json()
    except Exception as e:
        return f"Error fetching data: {e}"

    return render_template("gfApp.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)
