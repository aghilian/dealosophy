# Dealosophy Registration System

A simple registration system for Dealosophy that handles user registration and email notifications.

## Setup Instructions

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure email settings:
   - Open `server.py`
   - Update the following variables with your email settings:
     ```python
     SMTP_SERVER = "smtp.gmail.com"  # Your SMTP server
     SMTP_PORT = 587
     SMTP_USERNAME = "your-email@gmail.com"  # Your email
     SMTP_PASSWORD = "your-app-password"  # Your app password
     ```

3. Add your Dealosophy logo:
   - Place your logo file as `dealosophy_logo.png` in the same directory

4. Run the server:
```bash
python server.py
```

The server will start on port 5000. Access the registration page at `http://localhost:5000`

## Features

- Clean, responsive registration form
- Input validation for email and phone number
- Stores new registrations in `new_users.txt`
- Sends notification email to admin (iman@opensails.ca)
- Admin can approve registrations by replying with 'ok'
- Approved users are moved to `registered_users.txt`
- Welcome email sent to approved users

## File Format

### new_users.txt
```
timestamp|name|email|phone
```

### registered_users.txt
```
timestamp|name|email|phone
```

## Security Notes

- Make sure to use environment variables for sensitive information in production
- Consider adding rate limiting for the registration endpoint
- Use HTTPS in production
- Regularly backup the user files 