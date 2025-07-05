from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# === ENVIRONMENT VARIABLES ===
API_KEY_V3 = os.getenv('MAILERLITE_API_KEY')               # Used for v3 (subscribers)
API_KEY_V2 = os.getenv('MAILERLITE_API_KEY_V2') or API_KEY_V3  # Optional fallback
GROUP_ID = os.getenv('MAILERLITE_GROUP_ID')                # Used in both v2 & v3
VERIFIED_SENDER_EMAIL = os.getenv('MAILERLITE_SENDER_EMAIL')  # v2 sender email

# === HEADERS ===
V3_HEADERS = {
    'Authorization': f'Bearer {API_KEY_V3}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

V2_HEADERS = {
    'Content-Type': 'application/json',
    'X-MailerLite-ApiKey': API_KEY_V2
}

# === ROUTES ===

@app.route('/')
def home():
    return "📬 MailerLite Flask API (v2 & v3) is live!"


# === V3: Subscribe ===
@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    if not API_KEY_V3 or not GROUP_ID:
        logging.error("❌ Missing API key or Group ID")
        return jsonify({'error': 'Server misconfiguration'}), 500

    payload = {
        'email': email,
        'groups': [GROUP_ID]
    }

    try:
        response = requests.post(
            'https://connect.mailerlite.com/api/subscribers',
            headers=V3_HEADERS,
            json=payload
        )

        if response.status_code in (200, 201):
            logging.info(f"✅ Subscribed: {email}")
            return jsonify({'message': 'Successfully subscribed!'}), 200
        else:
            logging.warning(f"⚠️ MailerLite v3 error: {response.text}")
            return jsonify({'error': response.json().get('message', 'Subscription failed')}), response.status_code

    except Exception as e:
        logging.error(f"❌ Exception during subscription: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500


# === V2: Send Newsletter ===
@app.route('/send-newsletter', methods=['POST'])
def send_newsletter():
    data = request.get_json()
    subject = data.get('subject')
    html_content = data.get('html_content')

    if not subject or not html_content:
        return jsonify({'error': 'Subject and html_content are required'}), 400

    if not API_KEY_V2 or not GROUP_ID or not VERIFIED_SENDER_EMAIL:
        return jsonify({'error': 'Missing API key, group ID or verified sender email'}), 500

    try:
        # Step 1: Create campaign
        create_payload = {
            "subject": subject,
            "groups": [GROUP_ID],
            "from": {
                "email": VERIFIED_SENDER_EMAIL,
                "name": "Shanvilla Resort"
            },
            "type": "regular",
            "html": html_content
        }

        create_response = requests.post(
            "https://api.mailerlite.com/api/v2/campaigns",
            json=create_payload,
            headers=V2_HEADERS
        )
        create_response.raise_for_status()
        campaign_id = create_response.json().get("id")

        if not campaign_id:
            return jsonify({'error': 'Failed to create campaign'}), 500

        # Step 2: Send campaign
        send_url = f"https://api.mailerlite.com/api/v2/campaigns/{campaign_id}/actions/send"
        send_response = requests.post(send_url, headers=V2_HEADERS)
        send_response.raise_for_status()

        logging.info(f"📢 Newsletter sent — Campaign ID: {campaign_id}")
        return jsonify({'message': 'Newsletter sent successfully!'}), 200

    except requests.HTTPError as http_err:
        logging.error(f"❌ HTTP error: {http_err.response.text}")
        return jsonify({'error': 'MailerLite API error', 'details': http_err.response.text}), 500
    except Exception as e:
        logging.error(f"❌ Exception: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

