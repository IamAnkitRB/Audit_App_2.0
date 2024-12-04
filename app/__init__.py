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

    from app.routes.auth_routes import auth_bp
    from app.routes.hubspot_routes import hub_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')  
    app.register_blueprint(hub_bp, url_prefix='/hubspot')

    return app
