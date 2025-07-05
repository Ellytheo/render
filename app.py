from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os, logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv('MAILERLITE_API_KEY')
GROUP_ID = os.getenv('MAILERLITE_GROUP_ID')
BASE_URL = 'https://connect.mailerlite.com/api/subscribers'

HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

@app.route('/')
def home():
    return "MailerLite v3 Flask API is live!"

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    if not API_KEY or not GROUP_ID:
        logging.error("Missing MAILERLITE_API_KEY or MAILERLITE_GROUP_ID")
        return jsonify({'error': 'Server misconfiguration'}), 500

    payload = {
        'email': email,
        'groups': [GROUP_ID]
    }

    response = requests.post(BASE_URL, headers=HEADERS, json=payload)

    if response.status_code in (200, 201):
        logging.info(f"✅ Subscribed: {email}")
        return jsonify({'message': 'Successfully subscribed!'}), 200
    else:
        logging.warning(f"⚠️ MailerLite error: {response.text}")
        return jsonify({'error': response.json().get('message', 'Subscription failed')}), response.status_code
