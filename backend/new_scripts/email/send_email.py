import os
from dotenv import load_dotenv
load_dotenv()
import smtplib
from email.mime.text import MIMEText

def email_newsletter_to_user(html_formatted_email_string, recipient_email, recipient_name, today_date):
    print("sending email")
    sender_email = os.environ['GMAIL_APP_EMAIL']
    sender_password = os.environ['GMAIL_APP_PASSWORD']
    subject_line = f"{recipient_name}, your AI Daily Digest is here!"

    html_message = MIMEText(html_formatted_email_string, 'html')
    html_message['Subject'] = subject_line
    html_message['From'] = sender_email
    html_message['To'] = recipient_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, html_message.as_string())
        print(f"Email Sent to {recipient_email}!")