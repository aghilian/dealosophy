import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import os
import re
from config import EMAIL_USER, EMAIL_PASS, SMTP_SERVER, SMTP_PORT


def send_acknowledgment(receiver_email, has_attachment):
    """Sends an acknowledgment email based on attachment status."""
    
    # Create email message
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = receiver_email
    msg["Subject"] = "Acknowledgment: Your Work Order Received"

    # Email body
    if has_attachment:
        body = "We have received your work order and it is being processed."
    else:
        body = "We have received your email but couldn't find any files attached."

    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, receiver_email, msg.as_string())
        server.quit()

        print(f"📧 Acknowledgment email sent to {receiver_email}")

    except Exception as e:
        print(f"❌ Error sending email to {receiver_email}: {e}")



def format_as_html_table(extracted_data_text, filename):
    """Convert extracted financial data into structured HTML tables."""
    
    try:
        lines = extracted_data_text.strip().split("\n")
        structured_data = {}
        company_name = "Unknown Company"
        date_of_financial_info = "Unknown Date"
        years = []

        # Extract file name
        file_name = os.path.basename(filename)

        # Identify years and extract company name & date
        for line in lines:
            found_years = re.findall(r'\b(20\d{2})\b', line)
            years.extend([y for y in found_years if y not in years])
            
            if "Company Name" in line:
                company_name = line.split(":")[1].strip()
            if "Date of Financial Information" in line:
                date_of_financial_info = line.split(":")[1].strip()

        if not years:
            return "<p>⚠ No year-based financial data found.</p>"

        current_section = None
        for line in lines:
            line = line.strip()

            # Handle major section titles
            if line in ["Balance Sheet", "Statement of Income and Retained Earnings", "Liabilities", "Shareholders' Equity"]:
                current_section = line
                structured_data[current_section] = []

            elif ":" in line:  # Process key-value pairs
                parts = line.split(":")
                key = parts[0].strip()
                values = parts[1].split()

                # Convert values into dictionary format
                year_data = {}
                for i, year in enumerate(years):
                    if i < len(values):
                        value = values[i].replace(",", "").strip()
                        if value.replace(".", "").isdigit():  # Convert to integer if numeric
                            value = round(float(value) / 1000)  # ✅ Round to the nearest thousand
                        year_data[year] = value
                    else:
                        year_data[year] = ""

                structured_data[current_section].append([key] + [year_data.get(y, "") for y in years])

        # Generate separate tables for each financial section
        html_output = f"""
        <p><b>{file_name}</b></p>
        <p><b>Company:</b> {company_name}</p>
        <p><b>Financial Information as of:</b> {date_of_financial_info}</p>
        """

        for section, data in structured_data.items():
            df = pd.DataFrame(data, columns=["Category"] + years)
            df_html = df.to_html(index=False, border=1, justify="left", escape=False)
            html_output += f"<h3 style='text-align:center;'>{section}</h3>{df_html}"

        return html_output

    except Exception as e:
        print(f"❌ Error formatting data as a table: {e}")
        return f"<pre>{extracted_data_text}</pre>"  # Fallback to plain text if error occurs


def send_financial_report(receiver_email, extracted_data_text, filename):
    """Sends a structured financial report email with formatted tables and correct company name in the subject."""
    
    # Convert extracted data into an HTML table
    formatted_table = format_as_html_table(extracted_data_text, filename)

    # Extract company name for email subject
    company_name = "Unknown Company"
    for line in extracted_data_text.split("\n"):
        if "Company Name" in line:
            company_name = line.split(":")[1].strip()
            break

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = receiver_email
    msg["Subject"] = f"Financial Data for {company_name}"

    # Email body (HTML with proper table formatting)
    body = f"""
    <html>
    <body>
        <p>Dear User,</p>
        {formatted_table}  <!-- Insert structured table -->
        <p>Best regards,<br>Dealosophy Team</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(body, "html"))  # ✅ Send as HTML

    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, receiver_email, msg.as_string())
        server.quit()

        print(f"📊 Financial report email sent to {receiver_email}")

    except Exception as e:
        print(f"❌ Error sending financial report to {receiver_email}: {e}")
