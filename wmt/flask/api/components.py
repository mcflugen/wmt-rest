from flask import Blueprint
from flask import g, request, abort

from ..utils import as_resource, as_collection
from ..services import components, names, parameters
from ..core import deserialize_request

components_page = Blueprint('components', __name__)


@components_page.route('/', methods=['GET', 'OPTIONS'])
def show():
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    return components.jsonify_collection(components.all(sort=sort, order=order))


@components_page.route('/', methods=['POST'])
def add():
    data = deserialize_request(request, fields=['name', 'author', 'summary',
                                               'url', 'version', 'doi'])
    return components.create(**data).jsonify()


@components_page.route('/<int:id>', methods=['DELETE'])
def remove(id):
    component = components.get_or_404(id)
    components.delete(component)
    return '', 204


@components_page.route('/<int:id>', methods=['GET', 'OPTIONS'])
def component(id):
    return components.get_or_404(id).jsonify()


@components_page.route('/<int:id>/provides', methods=['GET'])
def get_provides(id):
    return components.jsonify_collection(components.get_or_404(id).provides)


@components_page.route('/<int:id>/provides', methods=['PATCH'])
def add_provides(id):
    component = components.get_or_404(id)

    data = deserialize_request(request, fields=['id'])
    name = names.get(data['id']) or abort(400)
    components.append(component, provides=name)

    return components.jsonify_collection(component.provides)


@components_page.route('/<int:id>/uses', methods=['GET'])
def get_uses(id):
    return components.jsonify_collection(components.get_or_404(id).uses)


@components_page.route('/<int:id>/uses', methods=['PATCH'])
def add_uses(id):
    component = components.get_or_404(id)

    data = deserialize_request(request, fields=['id'])
    name = names.get(data['id']) or abort(400)
    components.append(component, uses=name)

    return components.jsonify_collection(component.uses)


@components_page.route('/<int:id>/params', methods=['GET'])
def get_params(id):
    return components.jsonify_collection(components.get_or_404(id).parameters)


@components_page.route('/<int:id>/params', methods=['POST'])
def add_param(id):
    component = components.get_or_404(id)
    data = deserialize_request(request, fields=['key', 'description'])

    if not component.parameters.filter_by(key=data['key']).first():
        param = parameters.create(**data)
        components.append(component, parameters=param)

    return components.jsonify_collection(component.parameters)


@components_page.route('/<int:id>/params/<int:param_id>', methods=['DELETE'])
def remove_param(id, param_id):
    component = components.get_or_404(id)
    param = parameters.get(param_id) or abort(400)
    if param.component_id == id:
        parameters.delete(param)

    return components.jsonify_collection(component.parameters)


@components_page.route('/<int:id>/files', methods=['GET', 'OPTIONS'])
def files(id):
    return components.jsonify_collection(components.get_or_404(id).files)


@components_page.route('/<int:id>/files', methods=['POST'])
def add_file(id):
    component = components.get_or_404(id)
    data = deserialize_request(request, fields=['name', 'contents'])

    if not component.parameters.filter_by(key=data['name']).first():
        file = files.create(**data)
        components.append(component, files=file)

    return components.jsonify_collection(component.files)


@components_page.route('/<int:id>/files/<int:file_id>', methods=['DELETE'])
def remove_file(id, file_id):
    component = components.get_or_404(id)
    file = files.get(file_id) or abort(400)
    if files.component_id == id:
        files.delete(file)

    return components.jsonify_collection(component.files)
