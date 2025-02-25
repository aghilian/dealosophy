import imaplib
import email
import os
import re
from email.header import decode_header
from file_downloader import save_attachment
from email_sender import send_acknowledgment, send_financial_report
from config import EMAIL_USER, EMAIL_PASS, IMAP_SERVER, USER_FOLDER_PATH
# from chatgpt_processor import process_file_with_chatgpt

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
    match = re.search(r'<(.+?)>', sender)  # Looks for an email address inside <>
    return match.group(1) if match else sender.strip()  # If no <>, return as is

def parse_email(mail, email_id):
    """Fetches and parses an email by its ID."""
    res, msg_data = mail.fetch(email_id, "(RFC822)")
    for response in msg_data:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])
            sender = msg.get("From")
            subject, encoding = decode_header(msg["Subject"])[0]
            subject = subject.decode(encoding or "utf-8") if isinstance(subject, bytes) else subject

            sender_email = extract_email(sender)  # Extract clean email address
            print(f"📨 Parsed email from: {sender_email}")  # Debugging print
            return msg, sender_email, subject
    return None, None, None

def get_next_email_folder(sender):
    """Determines the next numbered folder for the sender."""
    if not sender.strip():  # Ensure sender is valid
        print("❌ ERROR: Sender email is empty! Skipping directory creation.")
        return None

    sender_folder = os.path.join(USER_FOLDER_PATH, sender)
    
    # 🛑 Debug: Print expected directory
    print(f"📁 Checking directory: {sender_folder}")

    if not os.path.exists(sender_folder):
        try:
            os.makedirs(sender_folder)
            print(f"📂 Created sender directory: {sender_folder}")
        except Exception as e:
            print(f"❌ ERROR: Failed to create sender directory {sender_folder}: {e}")
            return None

    # Find existing numbered folders
    existing_folders = [
        int(folder) for folder in os.listdir(sender_folder) if folder.isdigit()
    ]

    next_number = max(existing_folders, default=0) + 1  # Get next available folder number
    email_folder = os.path.join(sender_folder, str(next_number), "attachments")

    try:
        os.makedirs(email_folder)  # Create the folder
        print(f"📂 Created email folder: {email_folder}")
    except Exception as e:
        print(f"❌ ERROR: Failed to create email folder {email_folder}: {e}")
        return None

    return email_folder  # Return path where attachments should be saved

def process_attachments(msg, sender):
    """Extracts and processes attachments, returning extracted data."""
    extracted_data_list = []
    filename = None
    has_attachment = False

    # Determine next email folder for this sender
    email_folder = get_next_email_folder(sender)

    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    has_attachment = True
                    filepath = os.path.join(email_folder, filename)  # Save file to user's email folder
                    save_attachment(part, filepath)
                    extracted_data = None # process_file_with_chatgpt(filepath)
                    if extracted_data:
                        extracted_data_list.append(f"**{filename}**\n{extracted_data}")

    return has_attachment, extracted_data_list, filename

def process_email(mail, email_id):
    """Processes a single email: extracts data, sends acknowledgments, and reports."""
    msg, sender, subject = parse_email(mail, email_id)

    if not sender or not subject:
        print(f"⚠ Skipping email ID {email_id}, missing sender or subject.")
        return

    print(f"📨 Email from: {sender}, Subject: {subject}")

    # 🛑 Debug: Check if sender is valid
    if not sender.strip():
        print(f"❌ ERROR: Sender email is empty or invalid for email ID {email_id}")
        return

    has_attachment, extracted_data_list, filename = process_attachments(msg, sender)

    # Send acknowledgment email
    send_acknowledgment(sender, has_attachment)

    # Send financial report if extracted data exists
    if extracted_data_list and filename:
        extracted_data_text = "\n\n".join(extracted_data_list)
        send_financial_report(sender, extracted_data_text, filename)
    else:
        print(f"⚠ No valid extracted data found for {sender}, skipping report email.")


def fetch_unread_emails():
    """Main function to fetch and process unread emails."""
    print("🔍 Connecting to IMAP server...")
    mail = connect_email()

    print("📥 Checking for unread emails...")
    email_ids = get_unread_emails(mail)
    print(f"📧 Found {len(email_ids)} unread emails.")

    for email_id in email_ids:
        print(f"📩 Processing email ID: {email_id}")
        process_email(mail, email_id)

    mail.logout()
    print("✅ Finished processing all unread emails.")
