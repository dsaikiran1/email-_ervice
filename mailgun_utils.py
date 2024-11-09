# email_utils.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")

def send_email(to_email, subject, content, unique_id):
    """Send an email via Mailgun with tracking metadata."""
    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Your Name <mailgun@{MAILGUN_DOMAIN}>",
            "to": to_email,
            "subject": subject,
            "text": content,
            "o:tag": unique_id,  # Unique ID for tracking
            "o:tracking": "yes",
            "o:tracking-opens": "yes",
            "o:tracking-clicks": "yes",
        },
    )
    if response.status_code == 200:
        print(f"Email sent to {to_email}, ID: {unique_id}")
    else:
        print(f"Error sending email to {to_email}: {response.text}")
