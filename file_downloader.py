import os

# ATTACHMENTS_FOLDER = "attachments"
# os.makedirs(ATTACHMENTS_FOLDER, exist_ok=True)

def save_attachment(part, filepath):
    """Saves an email attachment and returns the file path."""
    if not filepath:  # ✅ Ensure filepath is valid
        print("❌ Error: Invalid filepath provided.")
        return None

    os.makedirs(os.path.dirname(filepath), exist_ok=True)  # ✅ Ensure directory exists before writing

    try:
        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))
        print(f"✅ Attachment saved: {filepath}")
        return filepath  # ✅ Return the correct file path
    except Exception as e:
        print(f"❌ Error saving attachment {filepath}: {e}")
        return None  # Return None if there's an error

