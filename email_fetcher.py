import imaplib
import email
import re
import subprocess
from email.header import decode_header
from email.utils import parsedate_to_datetime
from attachment_handler import process_attachments
from quick_feedback import send_acknowledgment
from config import EMAIL_USER, EMAIL_PASS, IMAP_SERVER
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_email():
    """Connects to the IMAP email server and selects the inbox."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        logging.info("Successfully connected to IMAP server.")
        return mail
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

# get the last email
def get_last_email(mail):
    """Fetches the latest email ID, whether read or unread."""
    status, messages = mail.search(None, 'ALL')  # ✅ Fetch all emails (both read & unread)
    email_ids = messages[0].split()

    if not email_ids:
        print("❌ No emails found.")
        return None  # No emails exist in the inbox

    last_email_id = email_ids[-1]  # ✅ Get only the last email
    return last_email_id

def get_unread_emails(mail):
    """Fetches unread email IDs from the inbox."""
    status, messages = mail.search(None, 'UNSEEN')
    return messages[0].split()  # List of unread email IDs

def extract_email(sender):
    """Extracts the actual email address from the sender string."""
    match = re.search(r'<(.+?)>', sender)
    return match.group(1) if match else sender.strip()

def parse_email(mail, email_id):
    """Fetches and processes an email."""
    res, msg_data = mail.fetch(email_id, "(RFC822)")
    logging.info("Starting email processing.")
    
    if not mail:
        logging.error("Failed to connect to IMAP server. Exiting.")
        return

    try:
        logging.info("Checking for unread emails...")
        email_ids = get_unread_emails(mail)
        logging.info(f"Found {len(email_ids)} unread emails.")

        for response in msg_data:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                sender = msg.get("From")
                subject, encoding = decode_header(msg["Subject"])[0]
                subject = subject.decode(encoding or "utf-8") if isinstance(subject, bytes) else subject

                user_email = extract_email(sender)
                print(f"📨 Processing email from: {user_email}")

                # Extract time of receipt
                received_time = msg.get("Date")
                if received_time:
                    received_time = parsedate_to_datetime(received_time).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    received_time = "Unknown Time"

                # Process attachments but only update history if attachments exist
                has_attachment, user_history_count = process_attachments(msg, user_email)

                message_id = msg.get("Message-ID")  # ✅ Extract the original Message-ID
                return user_email, subject, received_time, has_attachment, user_history_count, message_id
        
    except Exception as e:
        logging.error(f"An error occurred during email processing: {e}")
        if mail:
            try:
                mail.logout()
            except:
                pass

    return None, None, None, None, None, None

def process_all_emails():
    """Main function to process unread emails."""
    print("🔍 Connecting to IMAP server...")
    mail = connect_email()

    print("📥 Checking for unread emails...")
    email_ids = get_unread_emails(mail)
    # email_ids = get_last_email(mail)
    print(f"📧 Found {len(email_ids)} unread emails.")

    for email_id in email_ids:
        user_email, subject, received_time, has_attachment, user_history_count, message_id = parse_email(mail, email_id)
        if not user_email:
            print(f"⚠ Skipping email ID {email_id}, missing sender.")
            continue

        print(f"📨 Email from: {user_email}, Subject: {subject}, Received: {received_time}, Attachments: {has_attachment}, History: {user_history_count}")

        # Send acknowledgment email with subject and time
        send_acknowledgment(user_email, subject, received_time, has_attachment, message_id)
        
        # ✅ Call extract_data.py if the email has attachments
        if has_attachment:
            import subprocess
            # Pass message_id and subject to extract_data.py
            subprocess.run([
                "python", 
                "extract_data.py", 
                user_email, 
                str(user_history_count),
                message_id if message_id else "",  # Pass empty string if None
                subject if subject else ""         # Pass empty string if None
            ])
            print("🚣‍♀️ Message info sent to extract_data2.py", user_email, user_history_count, message_id, subject)
            

    mail.logout()
    print("✅ Finished processing all unread emails.")