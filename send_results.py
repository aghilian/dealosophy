from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
from email.message import EmailMessage
import base64
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CREDENTIALS_PATH = "/iman/dealosophy/credentials.json"  # Update with your path
TOKEN_PATH = "/iman/dealosophy/token.json"  # Update with your path

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

def create_message_with_attachment(sender, to, subject, message_text, file_path, in_reply_to=None, references=None):
    message = EmailMessage()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.set_content(message_text)

    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
    if references:
        message['References'] = references

    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(file_path)
            message.add_attachment(file_data, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file_name)
    except Exception as e:
        logging.error(f"Error attaching file: {e}")
        return None

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

def main():
    try:
        user_email = sys.argv[1]
        target_excel = sys.argv[2]
        message_id = sys.argv[3] if len(sys.argv) > 3 else None
        subject = sys.argv[4] if len(sys.argv) > 4 else None

        print("✝️ Message info received from json_to_excel2.py", user_email, target_excel, message_id, subject)

        if not os.path.exists(target_excel):
            print(f"❌ ERROR: The file {target_excel} does not exist. Cannot send email.")
            sys.exit()

        print(f"✅ File exists: {target_excel}")

        if subject:
            if not subject.startswith("Re:"):
                subject = f"Re: {subject}"
        else:
            subject = "Your processed results are ready for viewing"

        sender = "dealosophy.inbox@gmail.com"  # Replace with your Gmail address

        message_text = """Hi,\n\nYour processed results are attached.\n\nBest,\nDealosophy"""

        service = get_gmail_service()
        message = create_message_with_attachment(sender, user_email, subject, message_text, target_excel, message_id, message_id)

        if message:
            send_message(service, "me", message)

            if message_id:
                print(f"✅ Email successfully sent to {user_email} as a reply with attachment {os.path.basename(target_excel)}")
            else:
                print(f"✅ Email successfully sent to {user_email} with attachment {os.path.basename(target_excel)} (not as a reply)")

        print(f"DEBUG: message_id = {message_id}, subject = {subject}")

    except IndexError:
        print("Usage: python extract_data.py user_email target_excel [message_id] [subject]")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()