import imaplib
import email
from email.header import decode_header
import os
from file_downloader import save_attachment
from email_sender import send_acknowledgment, send_financial_report
from config import EMAIL_USER, EMAIL_PASS, IMAP_SERVER
from chatgpt_processor import process_file_with_chatgpt

def connect_email():
    """Connect to the email inbox and fetch unread emails."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    return mail

def fetch_unread_emails():
    """Fetch unread emails, download attachments, process them, and send acknowledgment."""
    print("🔍 Connecting to IMAP server...")
    mail = connect_email()
    
    print("📥 Checking for unread emails...")
    status, messages = mail.search(None, 'UNSEEN')
    
    email_ids = messages[0].split()
    print(f"📧 Found {len(email_ids)} unread emails.")

    for email_id in email_ids:
        print(f"📩 Processing email ID: {email_id}")
        res, msg = mail.fetch(email_id, "(RFC822)")
        
        for response in msg:
            if isinstance(response, tuple):
                # Parse email
                msg = email.message_from_bytes(response[1])
                sender = msg.get("From")
                subject, encoding = decode_header(msg["Subject"])[0]

                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")

                print(f"📨 Email from: {sender}, Subject: {subject}")

                has_attachment = False
                extracted_data_list = []
                filename = None  # ✅ Ensure filename is initialized

                if msg.is_multipart():
                    for part in msg.walk():
                        content_disposition = str(part.get("Content-Disposition"))
                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                has_attachment = True
                                filepath = save_attachment(part, filename)
                                extracted_data = process_file_with_chatgpt(filepath)  # ✅ Uses ChatGPT for PDF extraction

                                if extracted_data:
                                    extracted_data_list.append(f"**{filename}**\n{extracted_data}")

                # ✅ Send acknowledgment email
                send_acknowledgment(sender, has_attachment)

                # ✅ Send financial report only if data was extracted
                if extracted_data_list and filename:
                    extracted_data_text = "\n\n".join(extracted_data_list)
                    send_financial_report(sender, extracted_data_text, filename)
                else:
                    print(f"⚠ No valid extracted data found for {sender}, skipping report email.")

    mail.logout()
    print("✅ Finished processing all unread emails.")

if __name__ == "__main__":
    fetch_unread_emails()
