from flask import current_app

from ..core import Service, db
from .models import Parameter


class ParametersService(Service):
    __model__ = Parameter
