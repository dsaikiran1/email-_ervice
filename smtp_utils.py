# email_utils.py
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(to_email, subject, content, unique_id):
    """Send an email via SMTP with tracking details."""
    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    # Append a unique tracking pixel for open tracking
    tracking_pixel = f'<img src="https://yourserver.com/track_open?email_id={unique_id}" width="1" height="1" />'
    full_content = f"{content}\n\n{tracking_pixel}"
    msg.attach(MIMEText(full_content, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        print(f"Email sent to {to_email}, ID: {unique_id}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
