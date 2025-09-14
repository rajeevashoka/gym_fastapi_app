# test_smtp.py
import smtplib

def test_smtp_connection():
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login('nalanda.softwares@gmail.com', 'wckw rezw wubd qlqb')
        print("✅ SMTP connection successful!")
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_smtp_connection()