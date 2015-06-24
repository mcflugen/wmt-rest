from flask import current_app

from ..core import Service, db
from .models import Component



class ComponentsService(Service):
    __model__ = Component
