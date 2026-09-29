from flask import Flask, request, jsonify, send_from_directory, url_for
import os
from datetime import datetime
import re
from mailer import get_gmail_service, send_new_email, send_reply, process_email_attachments
import logging
import traceback
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('registration.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Ensure the log file has the correct permissions
try:
    if not os.path.exists('registration.log'):
        open('registration.log', 'a').close()
    os.chmod('registration.log', 0o666)  # Make it readable and writable by all
    logging.info("Logging initialized successfully")
except Exception as e:
    print(f"Warning: Could not set log file permissions: {e}")

app = Flask(__name__, static_folder='.')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Email configuration
ADMIN_EMAIL = "iman@opensails.ca"

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # North American phone number patterns:
    # 10 digits (e.g., 1234567890)
    # 11 digits starting with 1 (e.g., 11234567890)
    # Must be exactly 10 or 11 digits
    if len(phone) not in [10, 11]:
        return False
    
    # If 11 digits, must start with 1
    if len(phone) == 11 and phone[0] != '1':
        return False
    
    # Area code must be valid (200-999)
    area_code = phone[-10:][:3]
    if not (200 <= int(area_code) <= 999):
        return False
    
    return True

@app.route('/')
def serve_registration_page():
    try:
        return send_from_directory('.', 'register.html')
    except Exception as e:
        logging.error(f"Error serving registration page: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Failed to load registration page'}), 500

@app.route('/dealosophy_logo.png')
def serve_logo():
    try:
        return send_from_directory('.', 'dealosophy_logo.png')
    except Exception as e:
        logging.error(f"Error serving logo: {str(e)}")
        return jsonify({'error': 'Failed to load logo'}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        logging.info("Received registration request")
        data = request.get_json()
        logging.info(f"Registration data: {data}")
        
        if not data:
            logging.error("No JSON data received")
            return jsonify({'success': False, 'message': 'No data received'}), 400

        # Get and validate name
        name = data.get('name', '').strip()
        if not name:
            logging.warning("Name field is empty")
            return jsonify({'success': False, 'message': 'Name is required'}), 400
        if len(name) < 2:
            logging.warning(f"Name too short: {name}")
            return jsonify({'success': False, 'message': 'Name must be at least 2 characters long'}), 400

        # Get and validate email
        email = data.get('email', '').strip()
        if not email:
            logging.warning("Email field is empty")
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        if not is_valid_email(email):
            logging.warning(f"Invalid email format: {email}")
            return jsonify({'success': False, 'message': 'Please enter a valid email address'}), 400

        # Get and validate phone
        phone = data.get('phone', '').strip()
        if not phone:
            logging.warning("Phone field is empty")
            return jsonify({'success': False, 'message': 'Phone number is required'}), 400
        if not is_valid_phone(phone):
            logging.warning(f"Invalid phone format: {phone}")
            return jsonify({'success': False, 'message': 'Please enter a valid North American phone number'}), 400

        logging.info(f"Processing registration for: {name} ({email})")

        # Check if email already exists in registered_users.txt
        if os.path.exists('registered_users.txt'):
            with open('registered_users.txt', 'r') as f:
                if email in f.read():
                    logging.warning(f"Email already registered: {email}")
                    return jsonify({'success': False, 'message': 'This email is already registered'}), 400

        # Add to new_users.txt
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open('new_users.txt', 'a') as f:
                f.write(f"{timestamp}|{name}|{email}|{phone}\n")
            logging.info(f"Added user to new_users.txt: {email}")
        except Exception as e:
            logging.error(f"Error writing to new_users.txt: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to save registration'}), 500

        # Get Gmail service
        try:
            service = get_gmail_service()
            logging.info("Successfully obtained Gmail service")
        except Exception as e:
            logging.error(f"Failed to get Gmail service: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to initialize email service'}), 500

        # Send notification email to admin
        admin_subject = "New User Registration"
        admin_body = f"""
New user registration received:

Name: {name}
Email: {email}
Phone: {phone}
Timestamp: {timestamp}

To approve this registration, reply to this email with 'ok'.
"""
        try:
            if send_new_email(service, ADMIN_EMAIL, admin_subject, admin_body):
                logging.info(f"Successfully sent admin notification for: {email}")
                return jsonify({'success': True, 'message': 'Registration successful'})
            else:
                logging.error(f"Failed to send admin notification for: {email}")
                return jsonify({'success': False, 'message': 'Failed to send confirmation email'}), 500
        except Exception as e:
            logging.error(f"Error sending admin notification: {str(e)}")
            logging.error(traceback.format_exc())
            return jsonify({'success': False, 'message': 'Failed to send confirmation email'}), 500

    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/check_admin_reply', methods=['POST'])
def check_admin_reply():
    try:
        logging.info("Received admin reply check request")
        data = request.get_json()
        if not data:
            logging.error("No JSON data received in admin reply check")
            return jsonify({'success': False, 'message': 'No data received'}), 400

        email_content = data.get('email_content', '').strip()
        from_email = data.get('from_email', '').strip()
        
        logging.info(f"Processing admin reply from: {from_email}")
        logging.info(f"Email content: {email_content}")
        logging.info(f"Admin email configured as: {ADMIN_EMAIL}")
        
        # Normalize email addresses for comparison
        from_email = from_email.lower()
        admin_email = ADMIN_EMAIL.lower()
        
        logging.info(f"Comparing emails - From: {from_email}, Admin: {admin_email}")
        
        # Check if the email is from admin and contains 'ok'
        if from_email == admin_email and 'ok' in email_content.lower():
            logging.info("Admin approval detected")
            
            # Get the most recent registration from new_users.txt
            try:
                if not os.path.exists('new_users.txt'):
                    logging.error("new_users.txt does not exist")
                    return jsonify({'success': False, 'message': 'Registration data not found'}), 500
                    
                with open('new_users.txt', 'r') as f:
                    lines = f.readlines()
                
                if not lines:
                    logging.error("No pending registrations found")
                    return jsonify({'success': False, 'message': 'No pending registrations found'}), 400
                
                # Get the most recent registration
                latest_line = lines[-1].strip()
                timestamp, name, email, phone = latest_line.split('|')
                logging.info(f"Processing most recent registration: {email}")
                
                # Remove the approved user from new_users.txt
                with open('new_users.txt', 'w') as f:
                    f.writelines(lines[:-1])
                logging.info(f"Removed user from new_users.txt: {email}")
                
                # Add email to registered_users.txt
                with open('registered_users.txt', 'a') as f:
                    f.write(f"{email}\n")
                    logging.info(f"Added user email to registered_users.txt: {email}")
                
                # Get Gmail service
                try:
                    service = get_gmail_service()
                    logging.info("Successfully obtained Gmail service for welcome email")
                except Exception as e:
                    logging.error(f"Failed to get Gmail service: {str(e)}")
                    return jsonify({'success': False, 'message': 'Failed to initialize email service'}), 500
                
                # Send welcome email to user
                welcome_subject = "Welcome to Dealosophy!"
                welcome_body = f"""
Dear {name},

Welcome to Dealosophy! Your registration has been approved.

Here's what you can do next:
1. Log in to your account
2. Complete your profile
3. Start using Dealosophy's features

If you have any questions, please don't hesitate to contact us.

Best regards,
The Dealosophy Team
"""
                try:
                    if send_new_email(service, email, welcome_subject, welcome_body):
                        logging.info(f"Successfully sent welcome email to: {email}")
                        
                        # Send confirmation email to admin
                        admin_subject = "User Registration Approved"
                        admin_body = f"""
Dear Admin,

The following user has been approved and added to registered users:

Name: {name}
Email: {email}
Phone: {phone}
Timestamp: {timestamp}

The user has been removed from new_users.txt and added to registered_users.txt.
A welcome email has been sent to the user.

Best regards,
Dealosophy System
"""
                        if send_new_email(service, ADMIN_EMAIL, admin_subject, admin_body):
                            logging.info(f"Successfully sent confirmation email to admin: {ADMIN_EMAIL}")
                            return jsonify({'success': True, 'message': 'User approved and emails sent'})
                        else:
                            logging.error(f"Failed to send confirmation email to admin: {ADMIN_EMAIL}")
                            return jsonify({'success': False, 'message': 'Failed to send confirmation email'}), 500
                    else:
                        logging.error(f"Failed to send welcome email to: {email}")
                        return jsonify({'success': False, 'message': 'Failed to send welcome email'}), 500
                except Exception as e:
                    logging.error(f"Error sending emails: {str(e)}")
                    logging.error(traceback.format_exc())
                    return jsonify({'success': False, 'message': 'Failed to send emails'}), 500
                    
            except Exception as e:
                logging.error(f"Error processing registration: {str(e)}")
                logging.error(traceback.format_exc())
                return jsonify({'success': False, 'message': 'Failed to process registration'}), 500
        
        logging.warning(f"Invalid admin reply from: {from_email}")
        return jsonify({'success': False, 'message': 'Invalid approval email'}), 400

    except Exception as e:
        logging.error(f"Admin reply processing error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=5000, debug=False) 