from flask import Blueprint
from flask import json, jsonify
from flask import g, Response, request, abort
from flask import current_app

from ..core import deserialize_request
from ..utils import as_resource, jsonify_collection
from ..services import names


names_page = Blueprint('names', __name__)


def json_response(resp):
    return Response(json.dumps(resp, sort_keys=True, indent=2,
                               separators=(',', ': ')),
                   mimetype='application/json; charset=utf-8')


@names_page.route('/')
def show():
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    return names.jsonify_collection(names.all(sort=sort, order=order))


@names_page.route('/', methods=['POST'])
def add():
    data = deserialize_request(request, fields=['name'])
    name = names.first(name=data['name'])
    if name is None:
        name = names.create(data['name'])
    return name.jsonify()
    #return names.create(name=data['name']).jsonify()


@names_page.route('/<int:id>', methods=['DELETE'])
def remove(id):
    name = names.get_or_404(id)
    names.delete(name)
    return '', 204


@names_page.route('/<int:id>')
def name(id):
    name = names.get_or_404(id)
    return name.jsonify()


@names_page.route('/<int:id>/used', methods=['GET'])
def get_used_by(id):
    return names.jsonify_collection(names.get_or_404(id).components_that_use)


@names_page.route('/<int:id>/provided', methods=['GET'])
def get_provided_by(id):
    return names.jsonify_collection(names.get_or_404(id).components)


@names_page.route('/search')
def search():
    long_name = request.args.get('is', None)
    if long_name is None:
        return names.jsonify_collection(names.all())

    return names.jsonify_collection(names.find(name=long_name))

    contains = request.args.get('contains', None)
    if contains is not None:
        names_list = names.contains(contains)
    else:
        names_list = names.all()
    return names.jsonify_collection(names_list)
