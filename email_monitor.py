import os
import time
import json
import logging
import requests
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_monitor.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Reduce verbosity of Google API client logging
logging.getLogger('googleapiclient').setLevel(logging.WARNING)
logging.getLogger('google_auth_oauthlib').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Use the same scope as mailer.py
SCOPES = ['https://mail.google.com/']

def get_gmail_service():
    """Authenticate and return the Gmail service."""
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = credentials.Credentials.from_authorized_user_file('token.json')
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
                if os.path.exists('token.json'):
                    os.remove('token.json')
                
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save the new credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                logging.info("New credentials saved successfully")
            except Exception as e:
                logging.error(f"Error getting new credentials: {e}")
                raise
    
    return build('gmail', 'v1', credentials=creds)

def process_admin_reply(service, message):
    """Process an admin reply and call the check_admin_reply endpoint."""
    try:
        # Get the email content
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = msg['payload']['headers']
        
        # Get sender and subject
        from_email = next(h['value'] for h in headers if h['name'] == 'From')
        subject = next(h['value'] for h in headers if h['name'] == 'Subject')
        
        # Get the email body
        if 'parts' in msg['payload']:
            parts = msg['payload']['parts']
            data = parts[0]['body']['data']
            text = data.decode('base64')
        else:
            data = msg['payload']['body']['data']
            text = data.decode('base64')
        
        logging.info(f"Processing admin reply from: {from_email}")
        logging.info(f"Subject: {subject}")
        logging.info(f"Content: {text}")
        
        # Call the check_admin_reply endpoint
        response = requests.post(
            'http://localhost:5000/check_admin_reply',
            json={
                'email_content': text,
                'from_email': from_email
            }
        )
        
        if response.status_code == 200:
            logging.info("Successfully processed admin reply")
            # Mark the email as read
            service.users().messages().modify(
                userId='me',
                id=message['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logging.info(f"Marked email as read: {message['id']}")
        else:
            logging.error(f"Failed to process admin reply: {response.text}")
            
    except Exception as e:
        logging.error(f"Error processing admin reply: {str(e)}")

def monitor_inbox():
    """Monitor Gmail inbox for admin replies."""
    try:
        service = get_gmail_service()
        logging.info("Successfully obtained Gmail service")
        
        # Get the admin email from environment variable
        admin_email = os.getenv('ADMIN_EMAIL', 'iman@opensails.ca')
        
        while True:
            try:
                # Search for unread emails from admin
                query = f'from:{admin_email} is:unread'
                results = service.users().messages().list(userId='me', q=query).execute()
                messages = results.get('messages', [])
                
                if messages:
                    logging.info(f"Found {len(messages)} unread messages from admin")
                    for message in messages:
                        process_admin_reply(service, message)
                
                # Wait for 30 seconds before checking again
                time.sleep(30)
                
            except Exception as e:
                logging.error(f"Error in inbox monitoring loop: {str(e)}")
                time.sleep(30)  # Wait before retrying
                
    except Exception as e:
        logging.error(f"Failed to initialize Gmail service: {str(e)}")

if __name__ == '__main__':
    monitor_inbox() 