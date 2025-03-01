import smtplib
import email
import os
from email.message import EmailMessage
from config import EMAIL_USER, EMAIL_PASS  # Ensure your credentials are correct
import imaplib
import email
from email.mime.text import MIMEText
from email.header import decode_header

def send_acknowledgment(user_email, subject, received_time, has_attachment, original_msg_id=None):
    """
    Sends an acknowledgment email as a reply to the user's email.
    
    Parameters:
    - user_email: The email address of the recipient
    - subject: The subject of the original email
    - received_time: When the original email was received
    - has_attachment: Boolean indicating if attachments were found
    - original_msg_id: The Message-ID of the original email for proper threading
    """
    
    # ✅ Create the email
    msg = EmailMessage()
    
    # If subject doesn't already start with Re:, add it
    if subject and not subject.startswith("Re:"):
        msg["Subject"] = f"Re: {subject}"
    else:
        msg["Subject"] = subject if subject else "Re: Your email"
        
    msg["From"] = EMAIL_USER
    msg["To"] = user_email

    # ✅ Set reply headers for proper email threading
    if original_msg_id:
        msg["In-Reply-To"] = original_msg_id
        msg["References"] = original_msg_id

    # ✅ Email body
    if has_attachment:
        msg.set_content(f"""
Hi,

We have received your email and attachments. We will process them and get back to you soon.

Best,  
Dealosophy
""")
    else:
        msg.set_content(f"""
Hi,

We received an email from you but couldn't find any attachments.

Best,  
Dealosophy
""")

    # ✅ Send the email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"✅ Acknowledgment email successfully sent to {user_email}")
        if original_msg_id:
            print(f"✅ Email sent as a reply to Message-ID: {original_msg_id}")
        else:
            print("⚠️ Warning: Email sent as a new message (no original Message-ID provided)")
    except Exception as e:
        print(f"❌ ERROR: Failed to send acknowledgment email to {user_email}: {e}")