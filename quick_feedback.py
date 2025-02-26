import smtplib
from email.message import EmailMessage
from config import SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASS

def send_email(to_email, subject, body):
    """Sends an email using SMTP."""
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        print(f"✅ Email successfully sent to {to_email}")

    except Exception as e:
        print(f"❌ ERROR: Failed to send email to {to_email}: {e}")

def send_acknowledgment(user_email, subject, received_time, has_attachment):
    """Sends an acknowledgment email including subject and time of receipt."""
    print(f"📧 send_acknowledgment() called for {user_email}")

    if has_attachment:
        message = (
            f"📩 Subject: {subject}\n"
            f"📅 Received: {received_time}\n\n"
            "✅ We have received your email and attachments. We will process them and get back to you soon."
        )
    else:
        message = (
            f"📩 Subject: {subject}\n"
            f"📅 Received: {received_time}\n\n"
            "⚠ We received your email but could not find any attachments. "
            "If you intended to send attachments, please resend the email with them attached."
        )

    print(f"📧 Acknowledgment message prepared:\n{message}\n")

    # ✅ Send the email
    send_email(user_email, "Acknowledgment of Your Email", message)
