import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') 
    SQLALCHEMY_TRACK_MODIFICATIONS =  os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') 

    #JWT Secret
    SECRET_KEY =  os.getenv('SECRET_KEY') 

    # SMTP settings from environment variables
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  
    SENDER_EMAIL = os.getenv('SENDER_EMAIL') 
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')   
