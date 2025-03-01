import os
import smtplib
import sys
from email.message import EmailMessage
from config import EMAIL_USER, EMAIL_PASS  # Ensure credentials are correct

# Parse arguments
user_email = sys.argv[1]
target_excel = sys.argv[2]

# Optional arguments for reply functionality
message_id = sys.argv[3] if len(sys.argv) > 3 else None
subject = sys.argv[4] if len(sys.argv) > 4 else None

print("✝️ Message info received from json_to_excel2.py", user_email, target_excel, message_id, subject)
  
print(f"📤 Preparing to send email to {user_email}...")  # ✅ Debugging print

# ✅ Ensure the file exists
if not os.path.exists(target_excel):
    print(f"❌ ERROR: The file {target_excel} does not exist. Cannot send email.")
    sys.exit()  # Exit the module

print(f"✅ File exists: {target_excel}")  # ✅ Debugging print

# ✅ Create email
msg = EmailMessage()

# ✅ Set subject as reply to original subject if provided
if subject:
    if not subject.startswith("Re:"):
        msg["Subject"] = f"Re: {subject}"
    else:
        msg["Subject"] = subject
else:
    msg["Subject"] = "Your processed results are ready for viewing"
    
msg["From"] = EMAIL_USER
msg["To"] = user_email

# ✅ Set reply headers for proper email threading
if message_id:
    msg["In-Reply-To"] = message_id
    msg["References"] = message_id
    print(f"✅ Setting up as reply to Message-ID: {message_id}")

msg.set_content("""
Hi, 

Your processed results are attached. 

Best,  
Dealosophy
""")

# ✅ Attach Excel file
try:
    with open(target_excel, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(target_excel)
        msg.add_attachment(file_data, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file_name)

    print(f"📎 Attached file: {file_name}")  # ✅ Debugging print
except Exception as e:
    print(f"❌ ERROR: Could not attach file: {e}")
    sys.exit()  # Exit the module

# ✅ Send email
try:
    print("📡 Connecting to email server...")  # ✅ Debugging print
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:  # Update SMTP server if not using Gmail
        server.login(EMAIL_USER, EMAIL_PASS)
        print("✅ Logged into email server!")  # ✅ Debugging print
        server.send_message(msg)
    
    if message_id:
        print(f"✅ Email successfully sent to {user_email} as a reply with attachment {file_name}")
    else:
        print(f"✅ Email successfully sent to {user_email} with attachment {file_name} (not as a reply)")
except Exception as e:
    print(f"❌ ERROR: Failed to send email to {user_email}: {e}")

print(f"DEBUG: message_id = {message_id}, subject = {subject}")

