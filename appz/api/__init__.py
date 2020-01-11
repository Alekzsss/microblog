from flask import  Blueprint

bp = Blueprint('api', __name__)

from appz.api import users, posts, errors, tokens