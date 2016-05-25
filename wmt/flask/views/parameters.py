import os

from flask import Blueprint
from flask import json, url_for, current_app
from flask import g, request, abort, send_file
from flaskext.uploads import UploadSet

from ..utils import as_resource, as_collection
from ..db import sim as sim_db


parameters_page = Blueprint('parameters', __name__)
