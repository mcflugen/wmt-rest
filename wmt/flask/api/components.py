from flask import Blueprint
from flask import g, request, abort

from ..utils import as_resource, as_collection
from ..services import components, names, parameters
from ..core import deserialize_request

components_page = Blueprint('components', __name__)


#@components_page.route('/', methods=['GET', 'OPTIONS'])
#def show():
#    return as_collection(components.get_names(sort=True))
#    #return components.jsonify_collection(components.all(sort=sort, order=order))
#    #return components.jsonify_collection(components.all())


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
    #return components.create(name=data['name']).jsonify()
    #return models.create(data['name'], data['json'], owner=owner).jsonify()


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


#@components_page.route('/<name>', methods=['GET', 'OPTIONS'])
#def component(name):
#    key = request.args.get('key', None)
#
#    comp = components.get_or_404(name)
#
#    if key is not None:
#        return as_resource(comp.get(key, None) or abort(400))
#    else:
#        resp = {}
#        for key in ['doi', 'author', 'url', 'summary', 'version', 'id', ]:
#            resp[key] = comp[key]
#        return as_resource(resp)


@components_page.route('/<int:id>/params', methods=['GET'])
def get_params(id):
    return components.jsonify_collection(components.get_or_404(id).parameters)


@components_page.route('/<int:id>/params', methods=['PUT'])
def add_param(id):
    component = components.get_or_404(id)
    data = deserialize_request(request, fields=['id'])
    param = parameters.get(data['id']) or abort(400)
    components.append(component, parameters=param)

    return components.jsonify_collection(component.parameters)


@components_page.route('/<int:id>/params/<int:param_id>', methods=['DELETE'])
def remove_param(id, param_id):
    component = components.get_or_404(id)
    param = parameters.get(param_id) or abort(400)
    components.remove(component, parameters=param)

    return components.jsonify_collection(component.parameters)


@components_page.route('/<name>/params/<param>', methods=['GET'])
def component_param(name, param):
    comp = components.get_or_404(name)

    for p in comp['parameters']:
        if p['key'] == param:
            return as_resource(p)

    abort(404)


@components_page.route('/<name>/files', methods=['GET', 'OPTIONS'])
def component_files(name):
    return as_collection(components.input(name) or abort(404))


@components_page.route('/<name>/files/<file>', methods=['GET'])
def component_file(name, file):
    files = components.input(name) or abort(404)

    return as_resource(files.get(file, None) or abort(404))


@components_page.route('/<name>/inputs', methods=['GET'])
def component_inputs(name):
    comp = components.get_or_404(name)
    return as_resource(comp.get('uses', []))


@components_page.route('/<name>/outputs', methods=['GET'])
def component_outputs(name):
    comp = components.get_or_404(name)
    return as_resource(comp.get('provides', []))
