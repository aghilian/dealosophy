import os
import base64
from file_downloader import save_attachment  # Assuming you have this
from config import USER_FOLDER_PATH

def get_user_email_history(user_email):
    """Gets the count of emails with attachments by counting numeric subfolders."""
    sender_folder = os.path.join(USER_FOLDER_PATH, user_email)
    os.makedirs(sender_folder, exist_ok=True)
    existing_folders = [folder for folder in os.listdir(sender_folder) if folder.isdigit()]
    return len(existing_folders)

def get_next_email_folder(user_email):
    """Determines the next numbered folder for the sender and ensures all directories exist."""
    sender_folder = os.path.join(USER_FOLDER_PATH, user_email)
    os.makedirs(sender_folder, exist_ok=True)
    existing_folders = [int(folder) for folder in os.listdir(sender_folder) if folder.isdigit()]
    next_number = max(existing_folders, default=0) + 1
    email_folder = os.path.join(sender_folder, str(next_number), "attachments")
    os.makedirs(email_folder, exist_ok=True)
    return email_folder, next_number

def process_attachments(mime_msg, user_email):
    """Extracts and processes attachments from a MIME message (Gmail API format)."""
    has_attachment = False
    user_history_count = get_user_email_history(user_email)

    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    has_attachment = True
                    email_folder, new_history_count = get_next_email_folder(user_email)

                    # Save the attachment
                    try:
                        filepath = os.path.join(email_folder, filename)
                        save_attachment(part, filepath) #assuming save_attachment can work with a mime part.
                    except Exception as e:
                        print(f"Error saving attachment: {e}")

                    return True, new_history_count

    return False, user_history_count