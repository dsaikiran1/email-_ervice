import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
from gmail_utils import send_email_via_gmail
from email_utils import send_email, schedule_email, throttle_send_emails
from llm_utils import generate_content, create_custom_message
from sendgrid_utils import send_email_sendgrid,fetch_email_statuses
# Streamlit UI
st.title("AI Agent Dashboard")
st.sidebar.header("Upload a File or Connect to Google Sheets")

# Section 1: File Upload for CSV
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
uploaded_file = "emails.csv"  # Make sure this line is replaced with dynamic file upload
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of Uploaded Data:")
        st.dataframe(df.head())  # Show the first few rows
    except Exception as e:
        st.error(f"Error reading the uploaded CSV: {e}")

# Section 2: Google Sheets Connection
st.sidebar.subheader("Or Connect to Google Sheets")
google_sheet_url = st.sidebar.text_input("Enter Google Sheet URL")

if google_sheet_url:
    try:
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            "secrets/path_to_your_oauth_client_secret.json",  # Replace with your JSON file path
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

        # Authenticate and open the Google Sheet
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_url(google_sheet_url)
        worksheet = sheet.get_worksheet(0)  # Assuming you want the first sheet
        data = worksheet.get_all_records()

        # Convert the data to a DataFrame and display it
        df = pd.DataFrame(data)
        st.write("Preview of Google Sheet Data:")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")

# Initialize session state for the prompt template if not already set
if "email_prompt_template" not in st.session_state:
    st.session_state.email_prompt_template = f"Hello {df.columns[0]},\n\nWe would like to invite you to our event at . Please contact us at .\n\nBest regards,\nYour Company"

# Display buttons for each column
columns_per_row = 4  # Number of buttons per row
cols = st.columns(columns_per_row)

for i, col in enumerate(df.columns):
    placeholder = f"{{{col}}}"
    col_index = i % columns_per_row
    if cols[col_index].button(f"Insert {col}"):
        # Append the placeholder to the session state without resetting
        st.session_state.email_prompt_template += f" {placeholder}"

# Display editable email template
email_prompt_template = st.text_area(
    "Customize your email content template:",
    value=st.session_state.email_prompt_template,
    height=200,
    key="email_prompt_template"
)
subject = st.text_input("Subject")

# Step 3: Generate and Display Previews
if "previews" not in st.session_state:  # Initialize previews in session state if not already set
    st.session_state.previews = []

if st.button("Generate Previews"):
    st.write("Customized Email Previews:")
    st.session_state.previews.clear()  # Clear any previous previews

    # Generate previews for the first few recipients
    for index, row in df.iterrows():
        row_dict = row.to_dict()
        email_content = create_custom_message(email_prompt_template, row_dict)
        # Generate customized content for each recipient using LLM API
        generated_content = generate_content(subject+" "+email_content, row_dict)
        st.session_state.previews.append((row["Email"], generated_content))

        # Display only the first 3 previews
        if index < 3:
            st.write(f"Preview for {row['First name'] + ' ' + row['Last name']}:\n"
                     f"\n{generated_content}")
            st.write("---")

# Step 4: Schedule or Throttle Emails
email_scheduling = st.selectbox(
    "How would you like to schedule your emails?",
    options=["Immediately", "Scheduled Time", "Staggered over Interval"]
)

send_time = None
interval = None

if email_scheduling == "Scheduled Time":
    # Prompt the user to input the time for scheduling emails
    send_time = st.time_input("Select the time to send emails", value=datetime.strptime("09:00", "%H:%M").time())
elif email_scheduling == "Staggered over Interval":
    # Prompt the user to input the interval for staggering emails
    interval = st.number_input("Set the interval between emails (in minutes)", min_value=1, max_value=60, value=10)


# Initialize analytics data if not in session state
if "email_analytics" not in st.session_state:
    st.session_state.email_analytics = {
        "total_sent": 0,
        "pending": 0,
        "scheduled": 0,
        "failed": 0,
        "response_count": 0,
        "total_responses": 0  # Used for calculating response rate
    }
# Function to update real-time analytics
def update_email_count(success=True):
    if success:
        st.session_state.emails_sent += 1
    else:
        st.session_state.emails_failed += 1

    # Update pending count (This assumes that pending emails are being processed)
    st.session_state.emails_pending = len(df["Email"]) - st.session_state.emails_sent - st.session_state.emails_failed

    # Display email stats
    st.metric("Emails Sent", st.session_state.emails_sent)
    st.metric("Emails Failed", st.session_state.emails_failed)
    st.metric("Emails Pending", st.session_state.emails_pending)

# Step 5: Send Emails after Preview
email_service = st.selectbox("Select Email Service", ["Gmail", "SMTP", "SendGrid"])

if "Email" in df.columns:
    # Proceed with using the 'Email' column
    recipient_emails = df["Email"].tolist()
    st.write("Collected Email Addresses:")
    st.write(recipient_emails)
else:
    st.error("The DataFrame does not contain an 'Email' column.")

if st.button("Send Emails"):
    with st.spinner("Sending Emails..."):
        for (email, generated_content) in st.session_state.previews:  # Loop through previews with email and content

            # Choosing the email service and sending based on the selected service
            if email_service == "Gmail":
                send_email_function = send_email_via_gmail
           # elif email_service == "SMTP":
            #    send_email_function = send_email_smtp
            elif email_service == "SendGrid":
                send_email_function = send_email_sendgrid

            # Check if email scheduling is set
            if email_scheduling == "Scheduled Time":
                send_time_obj = datetime.strptime(send_time.strftime("%H:%M"), "%H:%M")
                if send_time_obj > datetime.now():
                    delay = (send_time_obj - datetime.now()).seconds
                    schedule_email(email, subject, generated_content, send_time.strftime("%H:%M"))
                    send_email_function(email, subject, generated_content)
                    st.success(f"Email scheduled for {email} at {send_time.strftime('%H:%M')}")
                else:
                    st.error(f"Cannot schedule time in the past for {email}.")
            elif email_scheduling == "Staggered over Interval":
                schedule_email(email, subject, generated_content, None, interval)
                send_email_function(email,subject,generated_content)
            else:
                send_email_function(email, subject, generated_content)
                st.success(f"Email sent to {email}")

            # Pause for throttling if not scheduled
            if email_scheduling != "Scheduled Time":
                time.sleep(1)  # Delay for throttling


def calculate_response_rate():
    if st.session_state.email_analytics["total_sent"] > 0:
        return (st.session_state.email_analytics["response_count"] / st.session_state.email_analytics["total_sent"]) * 100
    return 0

# Display email analytics as counters
st.header("Email Analytics Dashboard")
st.write("### Overview of Sent Emails")

# Display counters
st.metric("Total Emails Sent", st.session_state.email_analytics["total_sent"])
st.metric("Emails Pending", st.session_state.email_analytics["pending"])
st.metric("Emails Scheduled", st.session_state.email_analytics["scheduled"])
st.metric("Emails Failed", st.session_state.email_analytics["failed"])
st.metric("Response Rate (%)", f"{calculate_response_rate():.2f}%")

# Use Streamlit's chart functions for live updates (if data is sufficient)
st.write("### Sent Emails Over Time")
chart_data = pd.DataFrame({
    'Total Sent': [st.session_state.email_analytics["total_sent"]],
    'Failed': [st.session_state.email_analytics["failed"]],
    'Pending': [st.session_state.email_analytics["pending"]],
    'Scheduled': [st.session_state.email_analytics["scheduled"]],
}, index=[pd.Timestamp.now()])

line_chart = st.line_chart(chart_data)

# Update the chart at intervals (pseudo real-time)
for _ in range(5):
    # Simulate new data (in production, update with actual data)
    new_data = pd.DataFrame({
        'Total Sent': [st.session_state.email_analytics["total_sent"]],
        'Failed': [st.session_state.email_analytics["failed"]],
        'Pending': [st.session_state.email_analytics["pending"]],
        'Scheduled': [st.session_state.email_analytics["scheduled"]],
    }, index=[pd.Timestamp.now()])
    line_chart.add_rows(new_data)
    time.sleep(2)  # Adjust interval as needed

# Display email statuses
st.subheader("Email Statuses")
statuses = fetch_email_statuses()
st.write(statuses)