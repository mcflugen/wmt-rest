from flask import current_app

from ..core import Service, db
from .models import File


class FilesService(Service):
    __model__ = File
