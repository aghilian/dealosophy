from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import email
from email.utils import parseaddr
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

# load the list of registered users
def load_registered_users():
    """Loads registered user emails from a file."""
    registered_users = set()
    if os.path.exists("registered_users.txt"):
        with open("registered_users.txt", "r") as f:
            for line in f:
                email_address = line.strip().lower()
                if email_address:
                    registered_users.add(email_address)
    return registered_users
        
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
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
        msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_str)

        message_id = message['id']

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
            
            registered_users = load_registered_users()
            
            if sender_email.lower() not in registered_users:
                logging.info(f"⛔ Skipping email from unregistered user: {sender_email}")
                continue
            
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

        except Exception as e:
            logging.error(f"⚠ Skipping email ID {message_id}, could not retrieve email. Error: {e}")

    logging.info("✅ Finished processing all unread emails.")

if __name__ == '__main__':
    process_all_emails()