import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_attachment(part, filepath):
    """Saves an email attachment from a MIME part to the specified filepath."""

    if not filepath:
        logging.error("Invalid filepath provided.")
        return None

    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))

        logging.info(f"Attachment saved: {filepath}")
        return filepath

    except Exception as e:
        logging.error(f"Error saving attachment {filepath}: {e}")
        return None