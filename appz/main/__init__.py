from flask import Blueprint

bp = Blueprint('main', __name__)

from appz.main import routes