import os
import base64
import logging
import time
from email.message import EmailMessage
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import TOKEN_PATH, CREDENTIALS_PATH, BASE_DIR
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Reduce verbosity of Google API client logging
logging.getLogger('googleapiclient').setLevel(logging.WARNING)
logging.getLogger('google_auth_oauthlib').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

SCOPES = ['https://mail.google.com/']

def get_salutation():
    salutations = [
        "Hey champ! 🏆",
        "Hey rockstar! 🌟",
        "What's up, superstar? ✨",
        "Hey, genius! 🧠",
        "Hello, trailblazer! 🚀",
        "Hey, go-getter! 🎯",
        "Top of the day to you, champ! ☀️",
        "Ahoy, captain! ⚓",
        "Hey, fearless leader! 🦸",
        "Hey, game-changer! 🔥",
        "Hello, visionary! 👀",
        "Yo, mastermind! 🎩🃏",
        "Hey, superstar! 🌟",
        "What's up, mover & shaker? 💃🕺",
        "Hello, unstoppable force! 🌊",
        "Hey, big thinker! 🤔💭",
        "Hello, adventurer! 🗺️"
        "Hey, fearless explorer! 🧭"
        "Cheers, bold thinker! 🎩"
        "What's cookin', genius? 🍳"
        "Hey, architect of awesomeness! 🏗️"
        "Hello, maestro! 🎼"
        "Hey, boundary breaker! 🚧"
        "O, captain of cool! 🕶️"
                        
    ]
    return random.choice(salutations)

def get_gmail_service():
    """Authenticate and return the Gmail service."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            creds = credentials.Credentials.from_authorized_user_file(TOKEN_PATH)
        except Exception as e:
            logging.warning(f"Error loading credentials from token file: {e}")
            creds = None
    
    # If there are no (valid) credentials available, force the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.warning(f"Error refreshing credentials: {e}")
                # If refresh fails, force new authentication
                creds = None
        
        # If we still don't have valid credentials, get new ones
        if not creds:
            try:
                # Delete the existing token file if it exists
                if os.path.exists(TOKEN_PATH):
                    os.remove(TOKEN_PATH)
                
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save the new credentials
                with open(TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())
                logging.info("New credentials saved successfully")
            except Exception as e:
                logging.error(f"Error getting new credentials: {e}")
                raise
    
    return build('gmail', 'v1', credentials=creds)

def list_unread_messages(service, user_id='me'):
    """Lists unread email messages."""
    try:
        results = service.users().messages().list(userId=user_id, q='is:unread').execute()
        messages = results.get('messages', [])
        return messages
    except Exception as e:
        print(f"❌ Error listing unread messages: {e}")
        return []

def get_email_by_id(service, message_id, user_id='me'):
    """Fetch a specific email by its ID."""
    try:
        message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
        return message
    except Exception as e:
        print(f"Error fetching email with ID {message_id}: {e}")
        return None

def extract_email_details(message):
    """Extract email sender, subject, and message ID details."""
    headers = message['payload']['headers']
    sender, subject, message_id = None, None, None
    for header in headers:
        if header['name'].lower() == 'from':
            sender = header['value']
        elif header['name'].lower() == 'subject':
            subject = header['value']
        elif header['name'].lower() == 'message-id':
            message_id = header['value']
    return sender, subject, message_id

def mark_as_read(service, user_id, msg_id):
    """Marks the given message as read."""
    logging.info(f"Mark as read called with msg_id: {msg_id}")
    try:
        response = service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        logging.info(f"✅ Marked email ID {msg_id} as read. Full API Response: {response}")
        time.sleep(1) #Consider exponential backoff for large volumes.
    except HttpError as e:
        logging.error(f"❌ ERROR: HTTP Error marking email ID {msg_id} as read for user {user_id}: {e}")
    except Exception as e:
        logging.error(f"❌ ERROR: Failed to mark email ID {msg_id} as read for user {user_id}: {type(e)} - {e}")        
        
def send_reply(service, email_message, reply_text, attachment_paths=None):
    """
    Send a reply to an email with optional attachments.
    
    Args:
        service: Gmail API service instance
        email_message: The full email message object to reply to
        reply_text: The text content of the reply
        attachment_paths: List of file paths to attach (optional)
    
    Returns:
        Boolean indicating success
    """
    if email_message is None:
        print("❌ Email message is None. Cannot send reply.")
        return False
    
    # Extract email details
    headers = email_message['payload']['headers']
    
    subject, sender, message_id = None, None, None
    thread_id = email_message.get('threadId')
    
    if not thread_id:
        print("❌ No thread ID found in the email.")
        return False

    for header in headers:
        if header['name'].lower() == 'from':
            sender = header['value']
        elif header['name'].lower() == 'subject':
            subject = header['value']
        elif header['name'].lower() == 'message-id':
            message_id = header['value']

    if not sender:
        print("❌ No sender found in email headers.")
        return False

    # Create the reply email
    reply_msg = EmailMessage()
    reply_msg['To'] = sender
    reply_msg['Subject'] = "Re: " + (subject or "No Subject")
    if message_id:
        reply_msg['In-Reply-To'] = message_id  # Helps Gmail recognize it as a reply
        reply_msg['References'] = message_id  # Important for threading
    reply_msg.set_content(reply_text)

    # Attach files if provided
    if attachment_paths:
        for file_path in attachment_paths:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                    
                # Determine MIME type (simplistic approach)
                maintype = "application"
                subtype = "octet-stream"  # Default
                
                # Simple extension-based MIME type detection
                if file_name.endswith(".pdf"):
                    subtype = "pdf"
                elif file_name.endswith((".jpg", ".jpeg")):
                    maintype = "image"
                    subtype = "jpeg"
                elif file_name.endswith(".png"):
                    maintype = "image"
                    subtype = "png"
                elif file_name.endswith((".txt", ".md")):
                    maintype = "text"
                    subtype = "plain"
                elif file_name.endswith((".py", ".js", ".html", ".css")):
                    maintype = "text"
                    subtype = "plain"
                
                reply_msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
                print(f"✅ Added attachment: {file_name}")
            except FileNotFoundError:
                print(f"❌ File not found: {file_path}. Attachment not added.")
            except Exception as e:
                print(f"❌ Error attaching {file_path}: {e}")
    
    # Encode and send the reply within the same thread
    encoded_msg = base64.urlsafe_b64encode(reply_msg.as_bytes()).decode()
    message = {
        'raw': encoded_msg,
        'threadId': thread_id  # Ensure the reply stays in the same thread
    }

    try:
        service.users().messages().send(userId='me', body=message).execute()
        print(f"✅ Reply sent to {sender} in the same thread.")
        return True
    except Exception as e:
        print(f"❌ Error sending reply: {e}")
        return False

def send_new_email(service, to_address, subject, body_text, attachment_paths=None):
    """
    Send a new email (not a reply) with optional attachments.
    
    Args:
        service: Gmail API service instance
        to_address: Email address of the recipient
        subject: Subject line of the email
        body_text: The text content of the email
        attachment_paths: List of file paths to attach (optional)
    
    Returns:
        Boolean indicating success
    """
    # Create the email
    msg = EmailMessage()
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.set_content(body_text)

    # Attach files if provided
    if attachment_paths:
        for file_path in attachment_paths:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                    
                # Determine MIME type (simplistic approach)
                maintype = "application"
                subtype = "octet-stream"  # Default
                
                # Simple extension-based MIME type detection
                if file_name.endswith(".pdf"):
                    subtype = "pdf"
                elif file_name.endswith((".jpg", ".jpeg")):
                    maintype = "image"
                    subtype = "jpeg"
                elif file_name.endswith(".png"):
                    maintype = "image"
                    subtype = "png"
                elif file_name.endswith((".txt", ".md")):
                    maintype = "text"
                    subtype = "plain"
                elif file_name.endswith((".py", ".js", ".html", ".css")):
                    maintype = "text"
                    subtype = "plain"
                
                msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
                print(f"✅ Added attachment: {file_name}")
            except FileNotFoundError:
                print(f"❌ File not found: {file_path}. Attachment not added.")
            except Exception as e:
                print(f"❌ Error attaching {file_path}: {e}")
    
    # Encode and send the email
    encoded_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    message = {'raw': encoded_msg}

    try:
        service.users().messages().send(userId='me', body=message).execute()
        print(f"✅ Email sent to {to_address}.")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def process_email_attachments(service, email_message, user_email, base_dir):
    """
    Process attachments from Gmail API message format.
    
    Args:
        service: Gmail API service instance
        email_message: Gmail API message object
        user_email: Email address of the sender
        base_dir: Base directory for saving attachments
        
    Returns:
        tuple: (has_attachments, folder_count)
    """
    try:
        # Get existing folders to determine next folder number
        user_folder = os.path.join(base_dir, "users", user_email)
        os.makedirs(user_folder, exist_ok=True)
        
        existing_folders = [int(f) for f in os.listdir(user_folder) if f.isdigit()]
        folder_count = max(existing_folders, default=0) + 1
        
        # Check for attachments in the message
        if 'payload' not in email_message:
            return False, folder_count - 1
            
        parts = []
        if 'parts' in email_message['payload']:
            parts = email_message['payload']['parts']
        else:
            parts = [email_message['payload']]
            
        has_attachments = False
        
        for part in parts:
            if 'filename' in part and part['filename']:
                has_attachments = True
                # Create directories only when we find an attachment
                attachment_dir = os.path.join(user_folder, str(folder_count), "attachments")
                os.makedirs(attachment_dir, exist_ok=True)
                
                if 'body' in part and 'attachmentId' in part['body']:
                    att_id = part['body']['attachmentId']
                    filename = part['filename']
                    filepath = os.path.join(attachment_dir, filename)
                    
                    # Get the attachment content
                    att = service.users().messages().attachments().get(
                        userId='me',
                        messageId=email_message['id'],
                        id=att_id
                    ).execute()
                    
                    # Decode and save the attachment
                    data = base64.urlsafe_b64decode(att['data'])
                    with open(filepath, 'wb') as f:
                        f.write(data)
                    logging.info(f"✅ Saved attachment: {filename}")
        
        if has_attachments:
            return True, folder_count
        return False, folder_count - 1
        
    except Exception as e:
        logging.error(f"Error processing attachments: {e}")
        return False, 0