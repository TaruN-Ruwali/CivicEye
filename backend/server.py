from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import json
import os
from backend.ai_engine import verify_infrastructure_damage

app = Flask(__name__)
CORS(app)

# --- FIXED: Is line se file VS Code ke folder mein hi banegi ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'database.json')

# --- DATA LOAD KARNE KA FUNCTION ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return []

# --- DATA SAVE KARNE KA FUNCTION ---
def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"\n[SYSTEM] Data written to: {DB_FILE}") # Terminal check

# Server start hote hi purana data load hoga
db_reports = load_db()

@app.route('/')
def home():
    return "<h1>CivicEye Backend is LIVE with Persistent Storage!</h1>"

@app.route('/api/submit', methods=['POST'])
def handle_submission():
    try:
        address = request.form.get('address', '').strip()
        img = request.files.get('image')

        # Duplicate Check
        for r in db_reports:
            if r['address'].lower() == address.lower():
                # Duplicate par bhi success return kar rahe hain par reward 0
                return jsonify({"status": "Success", "ticket": r['id'], "reward": 0, "msg": "Duplicate"})

        is_ok, score = verify_infrastructure_damage(img)
        perc = round(score * 100, 2)

        if is_ok:
            tid = f"CIVIC-{random.randint(1000, 9999)}"
            new_report = {
                "id": tid,
                "address": address,
                "score": perc,
                "status": "SUBMITTED",
                "points": 10
            }
            db_reports.insert(0, new_report)
            
            #Data Save
            save_db(db_reports) 
            
            return jsonify({"status": "Success", "ticket": tid, "reward": 10})
        
        return jsonify({"status": "Fail", "msg": "AI Failed"}), 400
    except Exception as e:
        return jsonify({"status": "Error", "msg": str(e)}), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    return jsonify(db_reports)

if __name__ == "__main__":
    app.run(port=5000, debug=True)