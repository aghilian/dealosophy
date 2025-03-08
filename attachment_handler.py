import os
from file_downloader import save_attachment
from config import USER_FOLDER_PATH

def get_user_email_history(user_email):
    """Gets the count of emails with attachments by counting numeric subfolders."""
    sender_folder = os.path.join(USER_FOLDER_PATH, user_email)

    if not os.path.exists(sender_folder):
        return 0  # No previous emails with attachments

    existing_folders = [folder for folder in os.listdir(sender_folder) if folder.isdigit()]
    return len(existing_folders)

def get_next_email_folder(user_email):
    """Determines the next numbered folder for the sender, but only if there are attachments."""
    sender_folder = os.path.join(USER_FOLDER_PATH, user_email)

    if not os.path.exists(sender_folder):
        os.makedirs(sender_folder)

    # Find existing numeric folders
    existing_folders = [int(folder) for folder in os.listdir(sender_folder) if folder.isdigit()]
    next_number = max(existing_folders, default=0) + 1

    email_folder = os.path.join(sender_folder, str(next_number), "attachments")
    os.makedirs(email_folder, exist_ok=True)

    return email_folder, next_number  # ✅ Ensures two values are returned

def process_attachments(msg, user_email):
    """Extracts and processes all attachments in an email. Creates a folder and updates history if attachments exist."""
    has_attachment = False
    user_history_count = get_user_email_history(user_email)  # Get current count (before new email)
    saved_files = []  # Store saved file paths

    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    if not has_attachment:  
                        email_folder, new_history_count = get_next_email_folder(user_email)  # Create new folder
                        has_attachment = True  # Ensure folder is only created once

                    # Save each attachment in the newly created folder
                    filepath = os.path.join(email_folder, filename)
                    saved_path = save_attachment(part, filepath)
                    if saved_path:
                        saved_files.append(saved_path)

    return has_attachment, new_history_count if has_attachment else user_history_count, saved_files
