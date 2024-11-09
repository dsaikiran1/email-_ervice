# email_utils.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import sqlite3
import pandas as pd
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")


def send_email_sendgrid(to_email, subject, content, unique_id):
    """Send an email via SendGrid with tracking metadata."""
    message = Mail(
        from_email=os.getenv("SMTP_EMAIL"),
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )

    # Add unique ID to track each email
    message.custom_args = {"email_id": unique_id}  # Unique ID for tracking

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {to_email}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

# Function to fetch email statuses from the database
def fetch_email_statuses():
    with sqlite3.connect("email_status.db") as conn:
        statuses = pd.read_sql_query("SELECT * FROM email_status", conn)
    return statuses


def initialize_email_status_db():
    with sqlite3.connect("email_status.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_status (
                email_id TEXT PRIMARY KEY,
                to_email TEXT NOT NULL,
                subject TEXT,
                status TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()