# Email Tracking System with SMTP and Tracking Pixel

This project enables email tracking with **SMTP** by embedding a **tracking pixel** to detect when emails are opened. It also maintains a record of email delivery statuses (e.g., **Sent**, **Opened**, **Bounced**) in a SQLite database. A Streamlit dashboard displays these statuses in real-time, allowing for efficient monitoring.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Environment Variables](#environment-variables)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [License](#license)

## Features

- **SMTP Email Sending**: Send emails with unique tracking IDs for each recipient.
- **Open Tracking via Tracking Pixel**: Detects when an email is opened using a hidden pixel in the email content.
- **Database Storage**: Logs email statuses in a SQLite database for persistence.
- **Real-Time Dashboard**: Displays email delivery and open statuses on a Streamlit dashboard.

## Install Dependencies
- **pip install -r requirements.txt
- Set Up Environment Variables

- Create a .env file in the root directory and add your SMTP and email settings:

## Usage
- Start the Tracking Pixel Webhook Server
- The Flask server acts as a tracking pixel endpoint to log email opens. Run the following command to start the server:

- **python webhook.py

Note: The tracking pixel URL is embedded in each email as a 1x1 transparent image. When the recipient opens the email, the tracking pixel makes a request to the server, logging the email as "Opened."

### 2. Run the Email Dashboard in Streamlit
The Streamlit app provides an interface to upload recipient data, customize email templates, send emails, and view email statuses. Run the app with:

streamlit run app.py

### 3. Interact with the Dashboard
#### Upload CSV: Upload a CSV file containing recipient information (e.g., Name, Email).
- Customize Email Template: Define an email template with placeholders (e.g., {Name}) to personalize each message.
- Send Emails: Send emails to all recipients listed in the CSV file and track their status on the dashboard.
- View Statuses: The dashboard displays each email’s status, such as Sent, Opened, and Bounced.

### Limitations
- SMTP Limitations: SMTP doesn’t natively support advanced tracking events like "Delivered" or "Bounced." This project uses a tracking pixel to detect when an email is opened but does not detect delivery.
- Basic Bounce Handling: Bounces are not directly tracked but could be detected by using IMAP with a separate script to scan for undelivered emails.
- Privacy and Legal Compliance: Email tracking may have privacy implications, and laws around email tracking vary by region. Always notify users if tracking is enabled.

