import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_FROM_ADDRESS = os.environ.get('MAIL_FROM_ADDRESS')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['']
    SECURITY_EMAIL_SENDER = ''
    POSTS_PER_PAGE = 25
    IP_API = os.environ.get('API')
    RECAPTCHA_PUBLIC_KEY = os.environ.get('CAPTCHA_PUB')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('CAPTCHA_PRIV')