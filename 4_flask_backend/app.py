# 4_flask_backend/app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Storage file
DATA_FILE = os.path.join('data', 'alerts.json')

def load_alerts():
    """Load alerts from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_alerts(alerts):
    """Save alerts to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'message': 'Drowsiness Detection Backend is running'
    })

@app.route('/api/alert', methods=['POST'])
def receive_alert():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
        
        alerts = load_alerts()
        alert = {
            'id': len(alerts) + 1,
            'device_id': data.get('device_id', 'unknown'),
            'status': data.get('status', 'unknown'),
            'confidence': data.get('confidence', 0),
            'received_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        alerts.insert(0, alert) # Add to the beginning of the list
        save_alerts(alerts)
        
        print(f"🚨 ALERT RECEIVED: {alert['status']} (confidence: {alert['confidence']:.2f}) from {alert['device_id']}")
        
        return jsonify({'status': 'success', 'alert_id': alert['id']}), 200
    
    except Exception as e:
        print(f"Error processing alert: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    alerts = load_alerts()
    return jsonify({
        'alerts': alerts[:50], # Return latest 50 alerts
        'total_count': len(alerts)
    })

if __name__ == '__main__':
    print("Starting Drowsiness Detection Backend Server...")
    print("Dashboard available at http://127.0.0.1:5000")
    print("Listening for alerts on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)