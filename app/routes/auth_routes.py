from flask import Blueprint, request, jsonify
from app.services.auth_service import create_or_update_otp, generate_otp
from app.utils.email_service import send_otp_via_email
from app import db
from app.models.user import User
from datetime import datetime, timedelta
from app.services.auth_service import generate_jwt, decode_jwt

auth_bp = Blueprint('auth_bp', __name__)

# Route to request an OTP
@auth_bp.route('/request', methods=['POST'])
def request_otp():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"success":False, "error": "Email is required"}), 400

        otp, otp_record = create_or_update_otp(email)
        token = generate_jwt(email)

        if send_otp_via_email(email, otp):
            response = jsonify({"success":True, "message": "OTP sent successfully!", "token": token})
            response.set_cookie('token', token, httponly=True)
            return response, 200
        else:
            return jsonify({"success":False, "error": "Failed to send OTP"}), 500

    except Exception as e:
        return jsonify({"success":False, "error": str(e)}), 500

# Route to validate the OTP
@auth_bp.route('/validate', methods=['POST'])
def validate_otp():
    try:
        data = request.get_json()
        otp = data.get('otp')
        token = data.get('token')
        
        print(data)
        if not otp or not token:
            return jsonify({"success":False, "error": "OTP, and token are required"}), 400

        decoded_email = decode_jwt(token)
        if not decoded_email:
            return jsonify({"success":False, "error": "Invalid or expired token"}), 400

        otp_record = User.query.filter_by(email=decoded_email, otp=otp).first()

        if not otp_record:
            return jsonify({"success":False, "error": "Invalid OTP"}), 400

        if otp_record.expiration < datetime.now():
            return jsonify({"success":False, "error": "OTP has expired"}), 400
        
        if otp_record.validated:
            return jsonify({"success":False, "error": "Otp is already validated"}), 400
        
        otp_record.validated = True
        db.session.commit()

        return jsonify({"success": True,
            "message": "OTP validated successfully!"}), 200

    except Exception as e:
        return jsonify({"success":False,"error": str(e)}), 500


@auth_bp.route('/resend', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
           return jsonify({"success":False, "error": "Token is not provided"}), 400
        
        decoded_email = decode_jwt(token)

        otp_record = User.query.filter_by(email=decoded_email).order_by(User.id.desc()).first()
        
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
            otp_record = User(email=decoded_email, otp=otp, expiration=expiration)
            otp_record.validated = False
            db.session.add(otp_record)
            db.session.commit()  

        # Send the new OTP via email
        if send_otp_via_email(decoded_email, otp):
            token = generate_jwt(decoded_email)
            response = jsonify({"success":True, "message": "OTP resent successfully!", "token": token})
            response.set_cookie('token', token, httponly=True)
            return response, 200
        else:
            return jsonify({"success":False,"error": "Failed to send OTP"}), 500          


    except Exception as e:
        return jsonify({"success":False,"error": str(e)}), 500     

