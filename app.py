from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

app = Flask(__name__)
CORS(app)

# 🔐 Securely get MailerLite API key from environment
MAILERLITE_API_KEY = os.getenv('MAILERLITE_API_KEY')
MAILERLITE_BASE_URL = 'https://api.mailerlite.com/api/v2'

# 🔍 Set up logging
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

        url = f'{MAILERLITE_BASE_URL}/subscribers'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {MAILERLITE_API_KEY}'
        }
        payload = {
            'email': email
        }

        response = requests.post(url, json=payload, headers=headers)

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


