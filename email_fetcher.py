from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime, parseaddr
import re
import subprocess
import logging
import base64
import time
from attachment_handler import process_attachments
from quick_feedback import send_acknowledgment


CREDENTIALS_PATH = "/home/iman/dealosophy/credentials.json"  # Use absolute path
TOKEN_PATH = "/home/iman/dealosophy/token.json"  # Use absolute path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# keep a file of all processed emails

PROCESSED_EMAILS_FILE = "processed_emails.txt"

def load_processed_emails():
    """Loads processed email IDs from the file."""
    processed_emails = set()
    if os.path.exists(PROCESSED_EMAILS_FILE):
        with open(PROCESSED_EMAILS_FILE, "r") as f:
            for line in f:
                email_id = line.strip()
                if email_id:
                    processed_emails.add(email_id)
    return processed_emails

def save_processed_emails(processed_emails):
    """Saves processed email IDs to the file."""
    with open(PROCESSED_EMAILS_FILE, "w") as f:
        for email_id in processed_emails:
            f.write(f"{email_id}\n")

# only for registered users
def send_welcome_email(recipient_email):
    """Sends a welcome and onboarding email."""
    subject = "Welcome to Dealosophy!"
    message_text = """
    Welcome to Dealosophy! We're excited to have you on board.
    Here's how to get started...
    """
    #send_email(recipient_email, subject, message_text)  # You'll need to create this function

def send_waitlist_email(recipient_email):
    """Sends a waitlist email."""
    subject = "You're on the Dealosophy Waitlist"
    message_text = """
    Your email has been added to the wait list for Dealosophy.
    As we welcome new users, we will inform you to hop on board.
    """
    #send_email(recipientemail, subject, message_text)  # You'll need to create this function            
    
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

def mark_as_read(service, user_id, msg_id):
    """Marks the given message as read."""
    try:
        response = service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        logging.info(f"✅ Marked email ID {msg_id} as read. Full API Response: {response}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"❌ ERROR: Failed to mark email ID {msg_id} as read: {e}")
        
# Rest of your functions (process_attachments, send_acknowledgment) remain the same

def process_all_emails():
    """Fetches and processes unread emails from Gmail."""
    logging.info("📥 Checking for unread emails...")
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
    messages = results.get('messages', [])

    if not messages:
        logging.info("✅ No unread emails found.")
        return

    logging.info(f"📧 Found {len(messages)} unread emails.")

    processed_emails = load_processed_emails()

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
        msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_str)

        message_id = message['id']

        if message_id in processed_emails:
            logging.info(f"Email ID {message_id} already processed. Skipping.")
            continue

        try:
            parsed_email = {
                "from": mime_msg["From"],
                "subject": mime_msg["Subject"],
                "date": mime_msg["Date"],
                "message_id": mime_msg["Message-ID"]
            }

            sender_email = parseaddr(parsed_email["from"])[1]
            subject = parsed_email["subject"]
            message_id = parsed_email["message_id"]

            logging.info(f"📨 Processing email from: {sender_email}")

            user_history_count = 0  # Initialize user_history_count

            has_attachment, user_history_count = process_attachments(mime_msg, sender_email)

            if has_attachment:
                logging.info(f"📨 Email from: {sender_email}, Subject: {subject}, Received: {parsed_email['date']}, Attachments: True, History: {user_history_count}")

                message_id_reply = message_id.strip('<>').replace('\n','')

                send_acknowledgment(sender_email, subject, has_attachment, message_id_reply)
                subprocess.run(["python3", "extract_data.py", sender_email, str(user_history_count), message_id_reply, subject])
                logging.info(f"🚣‍♀️ Message info sent to extract_data.py {sender_email} {user_history_count} {message_id_reply} {subject}")
            mark_as_read(service, 'me', message['id'])

            processed_emails.add(message_id)
            save_processed_emails(processed_emails)

        except Exception as e:
            logging.error(f"⚠ Skipping email ID {message_id}, could not retrieve email. Error: {e}")

    logging.info("✅ Finished processing all unread emails.")

if __name__ == '__main__':
    process_all_emails()