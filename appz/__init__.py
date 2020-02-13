from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import Config
from elasticsearch import Elasticsearch
from redis import Redis
import rq
from flask_admin import Admin
from flask_babelex import Babel, lazy_gettext as _l


# workaround for babelex
from flask._compat import text_type
from flask.json import JSONEncoder as BaseEncoder
from speaklater import _LazyString

class JSONEncoder(BaseEncoder):
    def default(self, o):
        if isinstance(o, _LazyString):
            return text_type(o)
        return BaseEncoder.default(self, o)


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

from appz.admin import MyAdminIndexView

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    admin = Admin(app, 'Microblog', url='/', index_view=MyAdminIndexView(menu_icon_type='glyph', menu_icon_value='glyphicon-home'), template_mode='bootstrap3', category_icon_classes='glyph')
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)
    # workaround for flask-babelex
    app.json_encoder = JSONEncoder


    from appz.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from appz.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from appz.main import bp as main_bp
    app.register_blueprint(main_bp)

    from appz.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from appz.admin import init_admin
    init_admin(admin)

    if not app.debug and not app.testing:
        # send email with errors
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'], # fake email address here which is formed using the "no-reply" name and the email server
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # logging of programm
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

@babel.localeselector
def get_locale():
    # return 'es'
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
