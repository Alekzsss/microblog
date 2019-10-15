import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # config for email notification about errors
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = "alekzsss"
    MAIL_PASSWORD = "code1985"
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['alekzzzz3@outlook.com']
    # config for pagination
    POST_PER_PAGE = 25
    LANGUAGES = ['en', 'es', 'ru']

    # MS_TRANSLATOR_KEY = '5747bf9473ae47ebab8fef75923a2352'
    MS_TRANSLATOR_KEY = 'trnsl.1.1.20190803T212457Z.4b2ee7a5df36ce0f.b6a48d9825eb833a8098b37ca07d38c6aa121c3a'