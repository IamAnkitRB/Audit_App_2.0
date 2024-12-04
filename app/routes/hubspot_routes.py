
from flask import Blueprint, request, jsonify
from app.models.user import User


hub_bp = Blueprint('hub_bp', __name__)

# Route to request an OTP
@hub_bp.route('/get_code', methods=['GET'])
def get_code():
    code = request.args.get('code')
    try:
        print(f"Received code: {code}")
        # gen_token = FetchToken()
        # data = gen_token.save_auth_token(code)
        # session['access_token'] = data["access_token"]
        # session['refresh_token'] = data["refresh_token"]
        # session['time_stamp'] = data["time_stamp"]
        # return redirect('https://boundary.agency/hubspot-audit-generate-report')
    except Exception as e:
        return f"Error: {str(e)}"



