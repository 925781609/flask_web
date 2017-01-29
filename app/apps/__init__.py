from flask import Blueprint

apps = Blueprint('apps', __name__)

from . import views

