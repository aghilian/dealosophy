import os
import smtplib
import sys
from email.message import EmailMessage
from config import EMAIL_USER, EMAIL_PASS  # Ensure credentials are correct

def send_results(user_email, excel_file):
    """Sends the processed Excel file to the user via email."""
    
    print(f"📤 Preparing to send email to {user_email}...")  # ✅ Debugging print

    # ✅ Ensure the file exists
    if not os.path.exists(excel_file):
        print(f"❌ ERROR: The file {excel_file} does not exist. Cannot send email.")
        return

    print(f"✅ File exists: {excel_file}")  # ✅ Debugging print

    # ✅ Create email
    msg = EmailMessage()
    msg["Subject"] = "Your processed results are ready for viewing"
    msg["From"] = EMAIL_USER
    msg["To"] = user_email
    msg.set_content("""
Hi, 

Your processed results are attached. 

Best,  
Dealosophy
""")

    # ✅ Attach Excel file
    try:
        with open(excel_file, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(excel_file)
            msg.add_attachment(file_data, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file_name)

        print(f"📎 Attached file: {file_name}")  # ✅ Debugging print
    except Exception as e:
        print(f"❌ ERROR: Could not attach file: {e}")
        return

    # ✅ Send email
    try:
        print("📡 Connecting to email server...")  # ✅ Debugging print
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:  # Update SMTP server if not using Gmail
            server.login(EMAIL_USER, EMAIL_PASS)
            print("✅ Logged into email server!")  # ✅ Debugging print
            server.send_message(msg)
        print(f"✅ Email successfully sent to {user_email} with attachment {file_name}")
    except Exception as e:
        print(f"❌ ERROR: Failed to send email to {user_email}: {e}")

# ✅ Run the script with command-line arguments
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Missing arguments. Usage: send_results.py <user_email> <excel_file_path>")
        sys.exit(1)

    user_email = sys.argv[1]
    excel_file = sys.argv[2]
    send_results(user_email, excel_file)
