from flask import *
from flask_cors import CORS
import requests
import os
import logging

app = Flask(__name__)
CORS(app)

# Securely fetch MailerLite API key and Group ID from environment variables
MAILERLITE_API_KEY = os.getenv('MAILERLITE_API_KEY')
MAILERLITE_GROUP_ID = os.getenv('MAILERLITE_GROUP_ID')  # required for v3
MAILERLITE_BASE_URL = f'https://connect.mailerlite.com/api/groups/{MAILERLITE_GROUP_ID}/subscribers'

# Enable logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "Flask API is live!"

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        if not MAILERLITE_API_KEY or not MAILERLITE_GROUP_ID:
            return jsonify({'error': 'Missing API key or group ID'}), 500

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {MAILERLITE_API_KEY}'
        }
        payload = {
            'email': email
        }

        response = requests.post(MAILERLITE_BASE_URL, json=payload, headers=headers)

        if response.status_code in (200, 201):
            logging.info(f"Subscribed: {email}")
            return jsonify({'message': 'Successfully subscribed!'}), 200
        else:
            logging.warning(f"MailerLite error: {response.text}")
            return jsonify({
                'error': response.json().get('message', 'Subscription failed')
            }), response.status_code

    except Exception as e:
        logging.error(f"Exception in /subscribe: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

