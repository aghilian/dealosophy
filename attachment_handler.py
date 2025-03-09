import os
from file_downloader import save_attachment
from config import USER_FOLDER_PATH

def get_user_email_history(user_email):
    """Gets the count of emails with attachments by counting numeric subfolders."""
    sender_folder = os.path.join(USER_FOLDER_PATH, user_email)
    
    os.makedirs(sender_folder, exist_ok=True)  # ✅ Ensures the directory exists

    existing_folders = [folder for folder in os.listdir(sender_folder) if folder.isdigit()]
    return len(existing_folders)

def get_next_email_folder(user_email):
    """Determines the next numbered folder for the sender and ensures all directories exist."""
    sender_folder = os.path.join(USER_FOLDER_PATH, user_email)
    
    os.makedirs(sender_folder, exist_ok=True)  # ✅ Ensures the user folder exists

    # Find existing numeric folders
    existing_folders = [int(folder) for folder in os.listdir(sender_folder) if folder.isdigit()]
    next_number = max(existing_folders, default=0) + 1

    email_folder = os.path.join(sender_folder, str(next_number), "attachments")

    os.makedirs(email_folder, exist_ok=True)  # ✅ Ensures the attachment folder exists

    return email_folder, next_number

def process_attachments(msg, user_email):
    """Extracts and processes attachments. Only creates a folder and updates history if attachments exist."""
    has_attachment = False
    user_history_count = get_user_email_history(user_email)  # Get current count (before new email)

    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    has_attachment = True
                    email_folder, new_history_count = get_next_email_folder(user_email)  # Create new folder

                    # Save the attachment in the newly created folder
                    filepath = os.path.join(email_folder, filename)
                    save_attachment(part, filepath)

                    return True, new_history_count  # Return updated history count

    return False, user_history_count  # No folder created, return previous history count
