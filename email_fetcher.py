import imaplib
import email
import re
from email.header import decode_header
from email.utils import parsedate_to_datetime
from attachment_handler import process_attachments
from quick_feedback import send_acknowledgment
from config import EMAIL_USER, EMAIL_PASS, IMAP_SERVER

def connect_email():
    """Connects to the IMAP email server and selects the inbox."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    return mail

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

            return user_email, subject, received_time, has_attachment, user_history_count

    return None, None, None, None, None

def process_all_emails():
    """Main function to process unread emails."""
    print("🔍 Connecting to IMAP server...")
    mail = connect_email()

    print("📥 Checking for unread emails...")
    email_ids = get_unread_emails(mail)
    print(f"📧 Found {len(email_ids)} unread emails.")

    for email_id in email_ids:
        user_email, subject, received_time, has_attachment, user_history_count = parse_email(mail, email_id)

        if not user_email:
            print(f"⚠ Skipping email ID {email_id}, missing sender.")
            continue

        print(f"📨 Email from: {user_email}, Subject: {subject}, Received: {received_time}, Attachments: {has_attachment}, History: {user_history_count}")

        # Send acknowledgment email with subject and time
        send_acknowledgment(user_email, subject, received_time, has_attachment)

    mail.logout()
    print("✅ Finished processing all unread emails.")
