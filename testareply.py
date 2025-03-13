from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import base64
from email.message import EmailMessage

# Define paths for credentials and token
CREDENTIALS_PATH = 'credentials.json'
TOKEN_PATH = 'token.json'
SCOPES = ['https://mail.google.com/']

def get_gmail_service():
    """Authenticate and return the Gmail service."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = credentials.Credentials.from_authorized_user_file(TOKEN_PATH)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_latest_email(service, user_id='me'):
    """Fetch the latest email from the inbox."""
    try:
        results = service.users().messages().list(userId=user_id, maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No emails found in inbox.")
            return None

        message_id = messages[0]['id']
        print(f"Found message ID: {message_id}") #print the message ID.

        message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
        return message

    except Exception as e:
        print(f"Error fetching latest email: {e}")
        return None
    
def extract_email_details(message):
    """Extract email sender and subject details."""
    headers = message['payload']['headers']
    sender, subject, message_id = None, None, None
    for header in headers:
        if header['name'].lower() == 'from':
            sender = header['value']
            print(f"Found sender in extract_email_details: {sender}")
        elif header['name'].lower() == 'subject':
            subject = header['value']
        elif header['name'].lower() == 'message-id':
            message_id = header['value']
    return sender, subject, message_id

def send_reply(service, email_message):
    """Send a reply that stays in the same thread."""
    if email_message is None:
        print("email_message is None. Cannot send reply.")
        return
    
    print(email_message) # added print statement
    # Extract email details
    headers = email_message['payload']['headers']
    print("Headers:", headers)  # Add this debug print
    
    subject, sender, message_id, thread_id = None, None, None, email_message['threadId']
    thread_id = email_message.get('threadId')  # Use get() method
    print("Thread ID:", thread_id)  # Add this debug print
    
    if not thread_id:
        print("❌ No thread ID found in the email.")
        return

    for header in headers:
        if header['name'].lower() == 'from':
            sender = header['value']
            print(f"Found sender in send_reply: {sender}")
        elif header['name'].lower() == 'subject':
            subject = header['value']
            print(f"Found subject in send_reply: {subject}")
        elif header['name'].lower() == 'message-id':
            message_id = header['value']

    print(f"After header processing - Sender: {sender}, Subject: {subject}")
        
    if not sender:
        print("❌ No sender found in email headers.")
        return
    
    if not thread_id:
        print("❌ Could not extract sender or thread information.")
        return
    
    # Create the reply email
    reply_msg = EmailMessage()
    reply_msg['To'] = sender
    reply_msg['Subject'] = "Re: " + (subject or "No Subject")
    reply_msg['In-Reply-To'] = message_id  # Helps Gmail recognize it as a reply
    reply_msg['References'] = message_id  # Important for threading
    reply_msg.set_content("This is a reply.")

    # Attach a file
    try:
        with open("main.py", "rb") as f:
            file_data = f.read()
        reply_msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename="main.py")
    except FileNotFoundError:
        print("❌ main.py not found. Attachment not added.")
    except Exception as e:
        print(f"❌ Error attaching main.py: {e}")
        
        
    # Encode and send the reply within the same thread
    encoded_msg = base64.urlsafe_b64encode(reply_msg.as_bytes()).decode()
    message = {
        'raw': encoded_msg,
        'threadId': thread_id  # Ensure the reply stays in the same thread
    }

    service.users().messages().send(userId='me', body=message).execute()
    print(f"✅ Reply sent to {sender} in the same thread.")

def main():
    service = get_gmail_service()
    email_message = get_latest_email(service)
    if email_message:
        send_reply(service, email_message)  # Pass only service and the entire email_message object

if __name__ == '__main__':
    main()
