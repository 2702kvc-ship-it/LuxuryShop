import os
from urllib.parse import quote_plus


class Config:
    # Fail-fast for essential secrets to avoid accidental commits of defaults
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError('SECRET_KEY environment variable is required. Copy .env.example to .env and set SECRET_KEY.')

    # Thay thông tin đăng nhập SQL Server của bạn
    SERVER   = os.getenv('DB_SERVER', 'localhost')
    DATABASE = os.getenv('DB_NAME', 'LuxuryShop')
    USERNAME = os.getenv('DB_USERNAME', 'sa')
    PASSWORD = os.getenv('DB_PASSWORD')
    if not PASSWORD:
        raise RuntimeError('DB_PASSWORD environment variable is required. Do NOT commit real credentials.')
    DRIVER   = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{USERNAME}:{quote_plus(PASSWORD)}"
        f"@{SERVER}/{DATABASE}"
        f"?driver={quote_plus(DRIVER)}"
        f"trusted_connection=yes"  # Nếu dùng Windows Authentication, thêm tham số này và bỏ USERNAME/PASSWORD
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail — dùng Gmail
    MAIL_SERVER         = 'smtp.gmail.com'
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD       = os.getenv('MAIL_PASSWORD')
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        raise RuntimeError('MAIL_USERNAME and MAIL_PASSWORD environment variables are required for sending email.')
    MAIL_DEFAULT_SENDER = ('LuxuryShop', MAIL_USERNAME)