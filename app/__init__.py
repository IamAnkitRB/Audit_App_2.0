from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')  # Load the config from the config.py

    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "https://boundary.agency"}})

    from app.routes.auth_routes import otp_bp
    app.register_blueprint(otp_bp, url_prefix='/otp')  # Register routes

    return app
