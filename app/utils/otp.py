import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from app.core.config import settings

# In-memory OTP store (for development)
# In production, consider using Redis or a proper database
otp_store = {}

def generate_otp(length=6):
    """Generate a numeric OTP of specified length"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def store_otp(email: str, otp: str, expiry_minutes=10):
    """Store OTP with expiry time"""
    expiry_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    otp_store[email] = {
        "otp": otp,
        "expiry": expiry_time
    }

def get_otp(email: str):
    """Retrieve OTP from store"""
    return otp_store.get(email)

def delete_otp(email: str):
    """Remove OTP from store"""
    if email in otp_store:
        del otp_store[email]

def verify_otp(email: str, otp: str):
    """Verify if OTP is valid and not expired"""
    stored_data = get_otp(email)
    if not stored_data:
        return False
    
    if stored_data["expiry"] < datetime.utcnow():
        delete_otp(email)  # Clean up expired OTP
        return False
    
    if stored_data["otp"] == otp:
        delete_otp(email)  # Clean up used OTP
        return True
    
    return False

def send_email_otp(email: str, otp: str):
    """Send OTP to user's email"""
    if not all([settings.SMTP_SERVER, settings.SMTP_PORT, 
                settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
        print(f"Email configuration incomplete. Would send OTP {otp} to {email}")
        return
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = "Your Gym Management System Verification OTP"
        
        body = f"""
        <html>
            <body>
                <h2>Gym Management System - Email Verification</h2>
                <p>Your verification code is: <strong>{otp}</strong></p>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        print(settings.SMTP_SERVER, settings.SMTP_PORT,settings.SMTP_USERNAME, settings.SMTP_PASSWORD,settings.FROM_EMAIL)
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"OTP sent successfully to {email}")
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        # In development, we'll just print the OTP
        print(f"OTP for {email}: {otp}")


# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from random import randint

# from app.core import config

# # -------------------------------
# # Generate OTP
# # -------------------------------
# def generate_otp(length: int = 6) -> str:
#     """Generate a numeric OTP of given length"""
#     return "".join([str(randint(0, 9)) for _ in range(length)])


# # -------------------------------
# # Send OTP via email
# # -------------------------------
# def send_email_otp(email: str, otp: str):
#     """Send OTP email using SMTP"""
#     try:
#         # create email message
#         msg = MIMEMultipart()
#         msg['From'] = config.SMTP_EMAIL
#         msg['To'] = email
#         msg['Subject'] = "Your OTP for Gym Registration"

#         body = f"Your OTP code is: {otp}\nIt is valid for 5 minutes."
#         msg.attach(MIMEText(body, 'plain'))

#         # connect to SMTP server
#         server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
#         server.starttls()
#         server.login(config.SMTP_EMAIL, config.SMTP_PASSWORD)
#         server.send_message(msg)
#         server.quit()

#         print(f"✅ OTP {otp} sent to {email}")

#     except Exception as e:
#         print(f"❌ Failed to send OTP: {e}")
