import imaplib
import email
from email.header import decode_header
import sqlite3
import os


# Connect to the email account to fetch bounced messages
def check_bounced_emails():
    imap_server = "imap.gmail.com"
    email_account = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")

    # Connect to the inbox
    with imaplib.IMAP4_SSL(imap_server) as mail:
        mail.login(email_account, password)
        mail.select("inbox")

        # Search for emails with bounce-related subjects
        status, messages = mail.search(None, 'SUBJECT "Undelivered Mail Returned to Sender"')

        if status == "OK":
            for msg_num in messages[0].split():
                # Fetch the email by ID
                status, msg_data = mail.fetch(msg_num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    bounced_msg = part.get_payload(decode=True).decode()
                                    email_id = extract_email_id(bounced_msg)

                                    # Update bounce status in the database
                                    if email_id:
                                        with connect_db() as conn:
                                            conn.execute(
                                                "REPLACE INTO email_status (email_id, email, status) VALUES (?, ?, ?)",
                                                (email_id, extract_bounced_email(bounced_msg), "Bounced")
                                            )
                                    print(f"Bounce detected for {email_id}")


# Helper function to extract email ID from bounced message
def extract_email_id(bounced_msg):
    # Parse email ID or unique ID from the bounced message (customize this based on your implementation)
    return "email_id_from_bounced_message"
