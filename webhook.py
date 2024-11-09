# webhook.py
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Connect to database
def connect_db():
    return sqlite3.connect("email_status.db")

# Create table to store email statuses
def create_table():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS email_status (
                email_id TEXT PRIMARY KEY,
                email TEXT,
                status TEXT
            )
        """)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    email_id = data["tag"]
    event_type = data["event"]
    email = data["recipient"]

    # Update email status in the database
    with connect_db() as conn:
        conn.execute(
            "REPLACE INTO email_status (email_id, email, status) VALUES (?, ?, ?)",
            (email_id, email, event_type)
        )
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    create_table()
    app.run(port=5000)
