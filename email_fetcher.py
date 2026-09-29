import os
from email.utils import parseaddr
import logging
import base64
import mailer
import extract_data
import json_to_excel 
from config import BASE_DIR


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

def convert_to_mime_message(email_message):
    """Convert Gmail API message to email.message.Message object."""
    try:
        # Get the raw message data
        if 'raw' in email_message:
            raw_msg = base64.urlsafe_b64decode(email_message['raw'].encode('ASCII'))
        else:
            # If 'raw' is not available, try to get the message parts
            parts = []
            if 'payload' in email_message:
                if 'body' in email_message['payload']:
                    if 'data' in email_message['payload']['body']:
                        parts.append(email_message['payload']['body']['data'])
                if 'parts' in email_message['payload']:
                    for part in email_message['payload']['parts']:
                        if 'body' in part and 'data' in part['body']:
                            parts.append(part['body']['data'])
            
            if not parts:
                raise ValueError("No message content found")
            
            # Combine all parts and decode
            raw_msg = base64.urlsafe_b64decode(''.join(parts).encode('ASCII'))
        
        # Convert to email.message.Message object
        mime_msg = email.message_from_bytes(raw_msg)
        
        # Add headers from the original message if they're missing
        if 'payload' in email_message and 'headers' in email_message['payload']:
            for header in email_message['payload']['headers']:
                if not mime_msg[header['name']]:
                    mime_msg[header['name']] = header['value']
        
        return mime_msg
    except Exception as e:
        logging.error(f"Error converting message to MIME format: {e}")
        return None

def process_all_emails():
    """Fetches and processes unread emails from Gmail."""
    logging.info("📥 Checking for unread emails...")
    service = mailer.get_gmail_service()
    messages = mailer.list_unread_messages(service)

    if not messages:
        logging.info("✅ No unread emails found.")
        return

    logging.info(f"📧 Found {len(messages)} unread emails.")
    
    for message in messages:
        email_message = mailer.get_email_by_id(service, message['id'])
        if not email_message:
            logging.error(f"⚠ Could not retrieve email ID {message['id']}")
            continue

        try:
            # Extract email details
            sender, subject, message_id = mailer.extract_email_details(email_message)
            if not sender:
                logging.error("❌ Could not extract sender from email")
                continue

            sender_email = parseaddr(sender)[1]
            print(f"\nsender_from: {sender_email}")
            
            registered_users = load_registered_users()
            if sender_email.lower() not in registered_users:
                logging.info(f"⛔ Skipping email from unregistered user: {sender_email}")
                mailer.mark_as_read(service, 'me', message['id'])
                continue
            
            logging.info(f"📨 Processing email from: {sender_email}")

            # Process attachments using mailer's function
            has_attachment, user_history_count = mailer.process_email_attachments(
                service,
                email_message, 
                sender_email, 
                BASE_DIR
            )
            
            # Prepare the reply text based on whether there's an attachment
            random_salutation = mailer.get_salutation()
            if has_attachment:
                reply_text = f"{random_salutation}\n\nWe've received your email and attachments. Our 🤖 robots are working hard 🏗️ and will get back to you soon with the results. ✅🚀\n\nBest,\nDealosophy 🎯"
            else:
                reply_text = f"{random_salutation}\n\nWe received an email from you but couldn't find any attachments. 📂❌ Could you please check and resend them? 🔄\n\nBest,\nDealosophy"
                
            # Send the reply
            success = mailer.send_reply(service, email_message, reply_text)

            if success:
                logging.info(f"✅ Acknowledgment email successfully sent to {sender_email}")
            else:
                logging.error(f"❌ ERROR: Failed to send acknowledgment email to {sender_email}")

            if has_attachment:
                logging.info(f"📨 Email from: {sender_email}, Subject: {subject}, Received: {email_message['internalDate']}, Attachments: True, History: {user_history_count}")

                message_id_reply = message_id.strip('<>').replace('\n','')
                subject = subject.replace('\n','')
                print(f"{message_id_reply=}")
                print(f"{subject=}")

                # Start extracting data from all files in the attachment folder            
                print(f"Attempting to run extract_data.py with: {sender_email}, {user_history_count}, {message_id}, {subject}")
                extract_data.extractor(sender_email, str(user_history_count), message_id_reply)
                print("\n extract_data ran successfully")
                
                # Create an Excel file from the JSON files
                excel_file = json_to_excel.create_excel_file(os.path.join(BASE_DIR, "users", sender_email, str(user_history_count)))
                print(f"📊 Excel file created: {excel_file}")
                
                # Send the Excel file as an attachment
                random_salutation = mailer.get_salutation()
                reply_text = f"{random_salutation}\n\nGreat news! 🎉 Your data has been processed 🏗️🔍, and the results are ready! 📊✅\n\nWe've attached the results 📎📂—take a look and let us know if you have any questions! 💡🤓\n\nBest,\nDealosophy 🤖✨"
                
                # Only try to send with attachment if we have a valid file
                if excel_file:
                    mailer.send_reply(service, email_message, reply_text, [excel_file])
                else:
                    print("Warning: No Excel file was created. Sending email without attachment.")
                    mailer.send_reply(service, email_message, reply_text)

                logging.info(f"🚣‍♀️ Message info sent to extract_data.py {sender_email} {user_history_count} {message_id_reply} {subject}")
            
            # Mark the processed email as read    
            mailer.mark_as_read(service, 'me', message['id'])

        except Exception as e:
            print(f"message_id: {message['id']}")
            print(f"Exception: {e}")
            logging.error(f"⚠ Skipping email ID {message['id']}, could not process email. Error: {e}")

    logging.info("✅ Finished processing all unread emails.")

if __name__ == '__main__':
    process_all_emails()