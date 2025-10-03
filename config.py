
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # Formato: mysql+pymysql://usuario:password@host/base?charset=utf8mb4
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY__DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS','false')=='true'
