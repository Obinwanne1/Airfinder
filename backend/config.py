import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET = os.getenv('JWT_SECRET', 'dev-jwt-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///airfinder.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'Airfinder <noreply@airfinder.com>')

    MARKUP_PERCENT = float(os.getenv('DEFAULT_MARKUP_PERCENT', 8))
    SERVICE_FEE_USD = float(os.getenv('DEFAULT_SERVICE_FEE_USD', 15))
    COMMISSION_PERCENT = float(os.getenv('DEFAULT_COMMISSION_PERCENT', 3))

    SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL', 'admin@airfinder.com')
    SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD', 'Admin@2024!')

    PORT = int(os.getenv('PORT', 5000))
