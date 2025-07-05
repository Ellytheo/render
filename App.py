
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

MAILERLITE_API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiOTM2ZGZmOWIzNDFkMDIzNmYwNTcyMDI4YTJlNzViNGI2NzFhMzFhZGJhM2JhMDhhMjJiNTVjOGQyODk4M2JiNzgxMWU2NGIyNzM3OWY4MTciLCJpYXQiOjE3NTE2MjcyNDIuNDcyNjI2LCJuYmYiOjE3NTE2MjcyNDIuNDcyNjI4LCJleHAiOjQ5MDczMDA4NDIuNDY4MjcxLCJzdWIiOiIxNjU0NjYxIiwic2NvcGVzIjpbXX0.f8hNLEBCP5ZOW9mzn2LYaBOBYnjkpFM9quxchw4gTi1ya7hh5JLlqU1TkH5ZNP_NnC_onfDbHdj6FqWw6tulksQbCm4Rt5Mi6kShJVmqfPVHTB4LlF4aUghgHim15EoqVViEsZJF6NGJnKcWQhuGS807nb6wX65QjmcQXXliaI23Ft24Ug8fCU59wkzITh73rOpwECUMexSTMAMpUKBQNxygrzF0PBu0PLRSl638NmzoV18QMlYRxngwNaVgFncSQSR0S7Uy-OVEtdKAbT72v54cjtPwN0wKIoIyXJcAE3sCWYoypVLO1x7EoKd86sF67fuh6TUdnJzyKOb0KiuWQAhvnhEgBNPawQa48_42zIBt5tCAhN-pxyijFhGbkYPjkctMJQz5WdZX69R3-gDEGrQW6BvzTN4f_K9PhnPM3n4QQI3r1hNF7guJ_muYhXcp_LV5by9_RtvBpChqTKicqpjGN5BJ4NVHKyiSovITRUV6pNMCyZmf4NExRaMjha_pOlQLxT8p1Ch_4wqX2fU4H6ROXbjETVNaZcSrLBGllBtq1-yh4pfNKs8ZK7ONaMUbdbDEWib4ZY3834mUvUra6P_Ssy4A3fwPo6DYPBh28gaWylcteHFg-menIL3FEpv8dz4j3np89i-6qneyNTvHve24GY2j3OPnZyGxMIAA5L0'
MAILERLITE_BASE_URL = 'https://api.mailerlite.com/api/v2'

@app.route('/subscribe', methods=['POST'])
def subscribe():
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
        return jsonify({'message': 'Successfully subscribed!'}), 200
    else:
        return jsonify({
            'error': response.json().get('message', 'Subscription failed')
        }), response.status_code
