import random
import string
from datetime import datetime, timedelta
from app import db
from app.models.user import User

# Function to generate a 6-digit OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Function to create or update an OTP
def create_or_update_otp(email):
    otp = generate_otp()
    expiration = datetime.now() + timedelta(minutes=5)
    user_record = User.query.filter_by(email=email).first()

    if user_record:
        user_record.otp = otp
        user_record.expiration = expiration
        user_record.validated = False
        db.session.commit()
    else:
        user_record = User(email=email, otp=otp, expiration=expiration, validated=False)
        db.session.add(user_record)
        db.session.commit()

    return otp, user_record
