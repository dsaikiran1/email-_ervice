# email_utils.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import os
import schedule

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Email settings
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Function to send an email
def send_email(to_email, subject, body):
    """Send email using SMTP."""
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the server and send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USER, to_email, text)

# Function to handle email throttling and scheduling
def schedule_email(to_email, subject, body, send_time, interval=None):
    """
    Schedule emails with specific times and throttling.
    send_time: A string in the format 'HH:MM' for scheduled time.
    interval: Optional interval in minutes between emails (e.g., 10 minutes).
    """
    if interval:
        # If interval is provided, stagger emails
        schedule.every(interval).minutes.do(send_email, to_email, subject, body)
    else:
        # If specific time is given, schedule email for that time
        schedule.every().day.at(send_time).do(send_email, to_email, subject, body)

    # Keep the scheduler running in the background (in a separate thread or process)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Function to handle throttling
def throttle_send_emails(email_list, subject, body, max_emails_per_hour=50):
    """
    Throttle email sending to stay within provider limits.
    max_emails_per_hour: Number of emails to send per hour.
    """
    interval = 3600 / max_emails_per_hour  # Interval in seconds

    for email in email_list:
        send_email(email, subject, body)
        time.sleep(interval)  # Delay to throttle the rate of sending
