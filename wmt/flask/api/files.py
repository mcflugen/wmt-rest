import os

from flask import Blueprint
from flask import json, url_for, current_app
from flask import g, request, abort, send_file
from flask.ext.login import current_user, login_required

from ..utils import as_resource, as_collection
from ..errors import InvalidFieldError, AuthorizationError
from ..services import files, components
from ..core import deserialize_request


files_page = Blueprint('files', __name__)


@files_page.route('/')
def show():
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    return files.jsonify_collection(files.all(sort=sort, order=order))


@files_page.route('/', methods=['POST'])
def new():
    data = deserialize_request(request, fields=['name', 'contents',
                                                'component_id'])
    return files.create(**data).jsonify()


@files_page.route('/<int:id>', methods=['PATCH'])
def edit(id):
    data = deserialize_request(request,
                               fields=['name', 'contents', 'component'],
                               require='some')
    file = files.get_or_404(id)
    if 'component' in data:
        data['component_id'] = components.get_or_404(data.pop('component'))
    files.update(file, **data)
    return file.jsonify()


@files_page.route('/<int:id>')
def file(id):
    return files.get_or_404(id).jsonify()


@files_page.route('/<int:id>', methods=['DELETE'])
def delete(id):
    files.delete(files.get_or_404(id))
    return "", 204
