from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

app = Flask(__name__)
CORS(app)

# 🔐 Load MailerLite config from environment
MAILERLITE_API_KEY = os.getenv('MAILERLITE_API_KEY')
MAILERLITE_GROUP_ID = os.getenv('MAILERLITE_GROUP_ID')
MAILERLITE_BASE_URL = f'https://connect.mailerlite.com/api/groups/{MAILERLITE_GROUP_ID}/subscribers'

# 🔍 Enable logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "✅ MailerLite v3 Flask API is live!"

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        if not MAILERLITE_API_KEY or not MAILERLITE_GROUP_ID:
            logging.error("Missing MAILERLITE_API_KEY or MAILERLITE_GROUP_ID")
            return jsonify({'error': 'Server misconfiguration'}), 500

        headers = {
            'Authorization': f'Bearer {MAILERLITE_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'email': email
        }

        response = requests.post(MAILERLITE_BASE_URL, json=payload, headers=headers)

        if response.status_code in (200, 201):
            logging.info(f"✅ Subscribed: {email}")
            return jsonify({'message': 'Successfully subscribed!'}), 200
        else:
            logging.warning(f"⚠️ MailerLite error: {response.text}")
            return jsonify({'error': response.json().get('message', 'Subscription failed')}), response.status_code

    except Exception as e:
        logging.error(f"❌ Exception in /subscribe: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500
