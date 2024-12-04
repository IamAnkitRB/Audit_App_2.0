import smtplib
from app.config import Config

# Function to send OTP via email
def send_otp_via_email(email, otp):
    try:
        smtp_server = Config.SMTP_SERVER
        smtp_port = Config.SMTP_PORT
        sender_email = Config.SENDER_EMAIL 
        sender_password = Config.SENDER_PASSWORD  


        subject = "Your OTP Code"
        body = f"Your OTP code is: {otp}"
        message = f"Subject: {subject}\n\n{body}"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
