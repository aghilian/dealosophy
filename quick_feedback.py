import smtplib
import email
import os
from email.message import EmailMessage
from config import EMAIL_USER, EMAIL_PASS  # Ensure your credentials are correct

def send_acknowledgment(user_email, subject, received_time, has_attachment, original_msg_id=None):
    """Sends an acknowledgment email as a reply to the user's email."""
    
    # ✅ Create the email
    msg = EmailMessage()
    msg["Subject"] = f"Re: {subject}"  # ✅ Prefix subject with "Re:"
    msg["From"] = EMAIL_USER
    msg["To"] = user_email

    # ✅ Set reply headers
    if original_msg_id:
        msg["In-Reply-To"] = original_msg_id  # ✅ Link to original email
        msg["References"] = original_msg_id   # ✅ Maintain conversation thread

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
    except Exception as e:
        print(f"❌ ERROR: Failed to send acknowledgment email to {user_email}: {e}")

