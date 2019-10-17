from flask import Blueprint

bp = Blueprint('errors', __name__)

from appz.errors import handlers