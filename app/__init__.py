from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')  # Load the config from the config.py

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": "https://boundary.agency"}})

    from app.routes.auth_routes import otp_bp
    app.register_blueprint(otp_bp, url_prefix='/otp')  

    return app
