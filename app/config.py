import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql+pg8000://postgres:ankit@localhost/otpdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'  
