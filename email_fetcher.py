from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import re
import subprocess
import logging
from attachment_handler import process_attachments
from quick_feedback import send_acknowledgment

CREDENTIALS_PATH = "/iman/dealosophy/credentials.json"
TOKEN_PATH = "/iman/dealosophy/token.json"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = credentials.Credentials.from_authorized_user_file(TOKEN_PATH)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, ['https://mail.google.com/'], redirect_uri='http://localhost')
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f'Please visit this URL to authorize this application: {auth_url}')
            auth_code = input('Enter the authorization code: ')
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
        try:
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error writing token.json: {e}")
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_unread_messages(service, user_id='me'):
    try:
        results = service.users().messages().list(userId=user_id, q='is:unread').execute()
        messages = results.get('messages', [])
        return messages
    except Exception as e:
        logging.error(f"Error listing unread messages: {e}")
        return []

def get_message(service, user_id='me', msg_id=None):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_str)
        return mime_msg
    except Exception as e:
        logging.error(f"Error getting message: {e}")
        return None

def extract_email(sender):
    match = re.search(r'<(.+?)>', sender)
    return match.group(1) if match else sender.strip()

# Rest of your functions (process_attachments, send_acknowledgment) remain the same

def process_all_emails():
    print("🔍 Connecting to Gmail API...")
    service = get_gmail_service()

    print("📥 Checking for unread emails...")
    messages = list_unread_messages(service)
    print(f"📧 Found {len(messages)} unread emails.")

    for message in messages:
        mime_msg = get_message(service, msg_id=message['id'])
        if not mime_msg:
            print(f"⚠ Skipping email ID {message['id']}, could not retrieve email.")
            continue
        sender = mime_msg.get("From")
        subject, encoding = decode_header(mime_msg["Subject"])[0]
        subject = subject.decode(encoding or "utf-8") if isinstance(subject, bytes) else subject

        user_email = extract_email(sender)
        print(f"📨 Processing email from: {user_email}")

        received_time = mime_msg.get("Date")
        if received_time:
            received_time = parsedate_to_datetime(received_time).strftime('%Y-%m-%d %H:%M:%S')
        else:
            received_time = "Unknown Time"

        has_attachment, user_history_count = process_attachments(mime_msg, user_email)

        message_id = mime_msg.get("Message-ID")

        print(f"📨 Email from: {user_email}, Subject: {subject}, Received: {received_time}, Attachments: {has_attachment}, History: {user_history_count}")

        send_acknowledgment(user_email, subject, received_time, has_attachment, message_id)

        if has_attachment:
            subprocess.run([
                "python",
                "extract_data.py",
                user_email,
                str(user_history_count),
                message_id if message_id else "",
                subject if subject else ""
            ])
            print("🚣‍♀️ Message info sent to extract_data2.py", user_email, user_history_count, message_id, subject)

    print("✅ Finished processing all unread emails.")

if __name__ == '__main__':
    process_all_emails()