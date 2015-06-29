import os

from flask import Blueprint
from flask import json, url_for, current_app
from flask import g, request, abort, send_file
from flask.ext.login import current_user, login_required

from ..utils import as_resource, as_collection
from ..errors import InvalidFieldError, AuthorizationError
from ..services import parameters, components
from ..core import deserialize_request


parameters_page = Blueprint('parameters', __name__)


@parameters_page.route('/')
def show():
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    return parameters.jsonify_collection(parameters.all(sort=sort, order=order))


@parameters_page.route('/', methods=['POST'])
def new():
    data = deserialize_request(request, fields=['key', 'description', 'component_id'])
    return parameters.create(**data).jsonify()


@parameters_page.route('/<int:id>', methods=['PATCH'])
def edit(id):
    data = deserialize_request(request, fields=['key', 'description',
                                                'component'], require='some')
    param = parameters.get_or_404(id)
    if 'component' in data:
        data['component_id'] = components.get_or_404(data.pop('component'))
    parameters.update(param, **data)
    return param.jsonify()


@parameters_page.route('/<int:id>')
def parameter(id):
    return parameters.get_or_404(id).jsonify()


@parameters_page.route('/<int:id>', methods=['DELETE'])
def delete(id):
    parameters.delete(parameters.get_or_404(id))
    return "", 204
