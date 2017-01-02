from flask import Blueprint
print('start to register main blue print')
main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)
