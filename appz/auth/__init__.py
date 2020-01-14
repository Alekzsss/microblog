from flask import Blueprint
from flask_admin import Admin

bp = Blueprint('auth', __name__)
admin = Admin()

def create_module(app, **kwargs):
    admin

from appz.auth import routes