import smtplib
import random
import string
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://postgres:ankit@localhost/otpdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  

CORS(app, resources={r"/*": {"origins": "https://boundary.agency"}})
db = SQLAlchemy(app)

# OTP model for storing OTP data in the database
class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)
    validated = db.Column(db.Boolean, nullable= False, default=False)

    def __repr__(self):
        return f'<OTP {self.email}>'

with app.app_context():
    db.create_all()

# Function to generate a 6-digit OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Function to send OTP via SMTP
def send_otp_via_email(email, otp):
    try:
        smtp_server = "smtp.gmail.com"  
        smtp_port = 587
        sender_email = "ankit@boundary.agency" 
        sender_password = "iucx twvq zeii ynnq"  

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

# Function to generate JWT token
def generate_jwt(email):
    expiration = datetime.now() + timedelta(minutes=10)  
    payload = {
        'email': email,
        'exp': expiration
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Route to request an OTP
@app.route('/request_otp', methods=['POST'])
def request_otp():

    try:
        data = request.get_json()
        email = data.get('email')


        print('Received otp request for email :', email)
        

        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        otp_record = OTP.query.filter_by(email=email).first()

        if otp_record:
            # If OTP exists, update it
            otp = generate_otp()
            expiration = datetime.now() + timedelta(minutes=5)
            otp_record.otp = otp
            otp_record.expiration = expiration
            otp_record.validated= False
            db.session.commit()
            print('Updated OTP for email:', email)
        else:
            # If no OTP exists, create a new one
            otp = generate_otp()
            expiration = datetime.now() + timedelta(minutes=5)
            otp_record = OTP(email=email, otp=otp, expiration=expiration, validated= False)
            db.session.add(otp_record)
            db.session.commit()
            print('Created new OTP for email:', email)

        token = generate_jwt(email)

        if send_otp_via_email(email, otp):
            response = jsonify({"message": "OTP sent successfully!",
                                "token": token})
            response.set_cookie('token', token, httponly=True) 
            print('Successfully sent OTP to email::', otp) 
            return response, 200
        else:
            return jsonify({"error": "Failed to send OTP"}), 500
        
        

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to decode and verify JWT token
def decode_jwt(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['email']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Route to validate the OTP
@app.route('/validate_otp', methods=['POST'])
def validate_otp():
    try:
        data = request.get_json()
        otp = data.get('otp')
        token = data.get('token')

        if not otp or not token:
            return jsonify({"error": "Email, OTP, and token are required"}), 400

        decoded_email = decode_jwt(token)

        print('decoded email:::',decoded_email)
        if not decoded_email :
            return jsonify({"error": "Invalid or expired token"}), 400

        # Retrieve OTP record from the database
        otp_record = OTP.query.filter_by(email=decoded_email, otp=otp).first()

        if not otp_record:
            return jsonify({"error": "Invalid OTP"}), 400

        # Check if OTP has expired
        if otp_record.expiration < datetime.now():
            return jsonify({"error": "OTP has expired"}), 400
        
        if otp_record.validated == True:
            return jsonify({"error": "Otp is already validated"}), 400
        
        otp_record.validated = True
        db.session.commit()

        return jsonify({"message": "OTP validated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
           return jsonify({"error": "Token is not provided"}), 400
        
        decoded_email = decode_jwt(token)

        otp_record = OTP.query.filter_by(email=decoded_email).order_by(OTP.id.desc()).first()
        
        if otp_record:
                otp = generate_otp()
                expiration = datetime.now() + timedelta(minutes=5)
                otp_record.otp = otp
                otp_record.expiration = expiration
                otp_record.validated = False
                db.session.commit()
        else:
            otp = generate_otp()
            expiration = datetime.now() + timedelta(minutes=5)
            otp_record = OTP(email=decoded_email, otp=otp, expiration=expiration)
            otp_record.validated = False
            db.session.add(otp_record)
            db.session.commit()  

        # Send the new OTP via email
        if send_otp_via_email(decoded_email, otp):
            token = generate_jwt(decoded_email)
            response = jsonify({"message": "OTP resent successfully!", "token": token})
            response.set_cookie('token', token, httponly=True)
            return response, 200
        else:
            return jsonify({"error": "Failed to send OTP"}), 500          


    except Exception as e:
        return jsonify({"error": str(e)}), 500     

@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Logged out successfully"})
    response.delete_cookie('token') 
    return response, 200

if __name__ == '__main__':
    app.run(debug=True)
