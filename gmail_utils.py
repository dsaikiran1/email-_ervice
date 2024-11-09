import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import streamlit as st
from dotenv import load_dotenv  # Import dotenv to load .env variables

# Load environment variables from the .env file
load_dotenv()  # Loads the environment variables from .env

# Read the Gmail credentials file path from the environment variable
GMAIL_CLIENT_SECRET_PATH = os.getenv("GMAIL_CLIENT_SECRET_PATH")

# Scopes needed for sending email via Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def authenticate_gmail():
    creds = None
    # Check if the token.pickle file exists (used for storing user credentials)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials or they're expired, we need to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh expired credentials
        else:
            # Initiate OAuth2 flow using the credentials file from the .env
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CLIENT_SECRET_PATH, SCOPES)  # Use the credentials path from .env
            creds = flow.run_local_server(port=0)  # This will open a browser for user authentication

        # Save the credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def send_email_via_gmail(to_email, subject, body):
    creds = authenticate_gmail()  # Get the credentials
    try:
        # Build the Gmail API client with the authenticated credentials
        service = build('gmail', 'v1', credentials=creds)
        # Create the email message
        message = create_message('me', to_email, subject, body)
        # Send the message using the Gmail API
        send_message(service, 'me', message)
        st.success(f"Email sent to {to_email}")
    except Exception as error:
        st.error(f"An error occurred: {error}")


def create_message(sender, to, subject, body):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(body)  # Create the body of the email
    message.attach(msg)
    raw_message = message.as_string()  # Convert to string
    # Encode the message to base64 as required by Gmail API
    raw_message = base64.urlsafe_b64encode(raw_message.encode('utf-8')).decode('utf-8')
    return {'raw': raw_message}


def send_message(service, sender, message):
    try:
        # Send the email using Gmail API
        service.users().messages().send(userId=sender, body=message).execute()
    except Exception as error:
        print(f'An error occurred: {error}')
