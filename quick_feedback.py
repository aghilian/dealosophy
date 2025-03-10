from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
from email.message import EmailMessage
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CREDENTIALS_PATH = "/home/iman/dealosophy/credentials.json"  # Use absolute path
TOKEN_PATH = "/home/iman/dealosophy/token.json"  # Use absolute path

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

def create_message(sender, to, subject, message_text, in_reply_to=None, references=None):
    message = EmailMessage()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.set_content(message_text)

    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
    if references:
        message['References'] = references

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        logging.info(f"Message Id: {message['id']}")
        return message
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

def send_acknowledgment(user_email, subject, has_attachment, original_msg_id=None):
    """Sends an acknowledgment email using the Gmail API."""
    try:
        service = get_gmail_service()
        sender = "dealosophy.inbox@gmail.com"  # Replace with your Gmail address

        if subject and not subject.startswith("Re:"):
            subject = f"Re: {subject}"
        else:
            subject = subject if subject else "Re: Your email"

        if has_attachment:
            message_text = f"""Hi,\n\nWe have received your email and attachments. We will process them and get back to you soon.\n\nBest,\nDealosophy"""
        else:
            message_text = f"""Hi,\n\nWe received an email from you but couldn't find any attachments.\n\nBest,\nDealosophy"""

        message = create_message(sender, user_email, subject, message_text, original_msg_id, original_msg_id)
        send_message(service, "me", message)

        logging.info(f"✅ Acknowledgment email successfully sent to {user_email}")
        if original_msg_id:
            logging.info(f"✅ Email sent as a reply to Message-ID: {original_msg_id}")
        else:
            logging.warning("⚠️ Warning: Email sent as a new message (no original Message-ID provided)")

    except Exception as e:
        logging.error(f"❌ ERROR: Failed to send acknowledgment email to {user_email}: {e}")