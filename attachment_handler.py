import os
from config import USER_FOLDER_PATH
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_user_email_history(user_email):
    """Gets the highest numeric folder name (as an integer)."""
    sender_folder = os.path.join(USER_FOLDER_PATH, user_email)
    os.makedirs(sender_folder, exist_ok=True)
    existing_folders = []
    for folder in os.listdir(sender_folder):
        try:
            if folder.isdigit():
                existing_folders.append(int(folder))
        except ValueError:
            pass  # Ignore non-numeric folders

    if existing_folders:
        return max(existing_folders)
    else:
        return 0  # Return 0 if no numeric folders exist

def get_next_email_folder(user_email):
    """
    Determines the next numbered folder for the sender, ensures all directories exist,
    and returns the folder path and the next folder number.
    """
    sender_folder = os.path.join(USER_FOLDER_PATH, user_email)
    os.makedirs(sender_folder, exist_ok=True)
    next_number = get_user_email_history(user_email) + 1
    email_folder = os.path.join(sender_folder, str(next_number), "attachments")
    email_folder = os.path.expanduser(email_folder)  # Expand the tilde.
    os.makedirs(email_folder, exist_ok=True)
    logging.debug(f"Creating attachment folder: {email_folder}")
    return email_folder, next_number

def save_attachment(part, filepath):
    """Saves an attachment part to the specified filepath."""
    try:
        attachment_content = part.get_payload(decode=True)
        with open(filepath, 'wb') as f:
            f.write(attachment_content)
        logging.info(f"Attachment saved: {filepath}")
    except Exception as e:
        logging.error(f"Error saving attachment: {e}")

def process_attachments(mime_msg, user_email):
    """Extracts and processes attachments from a MIME message (Gmail API format)."""
    has_attachment = False
    user_history_count = get_user_email_history(user_email)
    email_folder, new_history_count = get_next_email_folder(user_email) #Call get_next_email_folder once.

    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    has_attachment = True
                    # Save the attachment
                    try:
                        filepath = os.path.join(email_folder, filename)
                        save_attachment(part, filepath)
                    except Exception as e:
                        logging.error(f"Error saving attachment: {e}")

    return has_attachment, new_history_count #use new_history_count