import requests

from flask import Blueprint, current_app, session
from flask import json, jsonify
from flask import g, request, url_for, session, render_template, flash, redirect
from flask.ext.login import current_user
#from flask.ext.openid import OpenID
from flask_login import login_user, logout_user

from openid.extensions import pape

from ..services import users
from ..models.models import Model
from ..utils import as_resource, as_collection
from ..errors import (AuthenticationError, AlreadyExistsError,
                      MissingFieldError, InvalidJsonError)
from ..core import deserialize_request


users_page = Blueprint('users', __name__)

#oid = OpenID(current_app, safe_roots=[], extension_responses=[pape.Response])


class User(object):
    def __init__(self, id):
        self._id = id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id


#from wmt_wsgi import oid

from flask_oauth import OAuth, OAuthRemoteApp, OAuthException, parse_response


class MWOAuthRemoteApp(OAuthRemoteApp):
     def handle_oauth1_response(self):
        """Handles an oauth1 authorization response.  The return value of
        this method is forwarded as first argument to the handling view
        function.
        """
        client = self.make_client()
        resp, content = client.request('%s&oauth_verifier=%s' % (
            self.expand_url(self.access_token_url),
            request.args['oauth_verifier'],
        ), self.access_token_method)
        print resp, content
        data = parse_response(resp, content)
        if not self.status_okay(resp):
            raise OAuthException('Invalid response from ' + self.name,
                                 type='invalid_response', data=data)
        return data


oauth = OAuth()
csdms = MWOAuthRemoteApp(
    oauth,
    'csdms',
    base_url='http://csdms.colorado.edu',
    request_token_url='http://csdms.colorado.edu/w/index.php',
    request_token_params = {'title': 'Special:OAuth/initiate',
                            'oauth_callback': 'oob'},
    access_token_url='http://csdms.colorado.edu/w/index.php?title=Special:OAuth/token',
    authorize_url='http://csdms.colorado.edu/wiki/Special:OAuth/authorize',

    # WMT-Web
    #consumer_key='7569b56adf97d65804bdec76424f92d4',
    #consumer_secret='d0ce83bcc938cba964cdb96d7411e752c6c7a580',

    # WMT
    consumer_key='a548a9eec46cbb1333ef0d7eed4c9b46',
    consumer_secret='2fa73c563aff08173c4190062d453c851a008bab',
)
oauth.remote_apps['csdms'] = csdms


@csdms.tokengetter
def get_mwo_token(token=None):
    return session.get('mwo_token')


@users_page.route('/logout')
def logout():
    session['mwo_token'] = None
    session['username'] = None
    if 'next' in request.args:
        return redirect(request.args['next'])
    return 'Logged out!'


@users_page.route('/login')
def login():
    redirector = csdms.authorize()

    if 'next' in request.args:
        oauth_token = session[csdms.name + '_oauthtok'][0]
        session[oauth_token + '_target'] = request.args['next']

    redirector.headers['Location'] += '&oauth_consumer_key=' + csdms.consumer_key
    return redirector
    #return csdms.authorize()
    #return csdms.authorize(callback=url_for('users.oauth_authorized',
    #                                        next=request.args.get('next') or request.referrer or None))


#@users_page.route('/oauth-callback')
@users_page.route('/')
@csdms.authorized_handler
def oauth_authorized(resp):
    next_url_key = request.args['oauth_token'] + '_target'
    default_url = url_for('users.whoami')

    next_url = session.pop(next_url_key, default_url)

    if resp is None:
        raise ValueError('unable to authorize')
        return redirect(next_url)

    try:
        session['mwo_token'] = (
            resp['oauth_token'],
            resp['oauth_token_secret']
        )
    except KeyError:
        raise ValueError(resp)

    #session['csdms_user'] = resp['screen_name']
    session['csdms_user'] = get_current_user(cached=False)

    g.user = users.first(username=session['csdms_user'])

    if g.user is None:
        g.user = users.create(session['csdms_user'], session['csdms_user'])

    return redirect(next_url)


def query(api_query, url=None):
    """ e.g. {'action': 'query', 'meta': 'userinfo'}. format=json not required
        function returns a python dict that resembles the api's json response
    """
    import urllib

    api_query['format'] = 'json'
    url = url or 'http://csdms.colorado.edu/w'

    #return requests.post('http://csdms.colorado.edu/w/api.php?action=query&meta=userinfo&uiprop=email&format=json').json()
    return csdms.post(url + "/api.php?" + urllib.urlencode(api_query),
                      content_type="text/plain").data


def get_current_user(cached=True):
    if cached:
        return session.get('username')

    try:
        data = query({'action': 'query', 'meta': 'userinfo', 'uiprop': 'email'})
        #raise ValueError(data['query']['userinfo'])
        session['username'] = get_user_email(data['query']['userinfo']['name'])
    except KeyError:
        #raise ValueError((data['query']['userinfo'].keys(),
        #                  data['query']['userinfo']['name']))
        session['username'] = None
        if data['error']['code'] == "mwoauth-invalid-authorization":
            flash(u'Access to this application was revoked. Please re-login!')
        else:
            raise
    except OAuthException:
        session['username'] = None
    return session['username']


def get_user_email(user):
    import urllib

    url = 'http://csdms.colorado.edu/w'
    api_query = {
        'action': 'ask',
        'query': '[[User:%s]]|?Confirm email member' % user,
        'format': 'json'
    }
    resp = requests.get(url + '/api.php?' + urllib.urlencode(api_query)).json()

    email = resp['query']['results']['User:%s' % user]['printouts']['Confirm email member'][0]

    return email.split(':')[-1]


@users_page.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        #g.user = User.query.filter_by(openid=session['openid']).first()
        g.user = users.first(openid=session['openid'])


#@users_page.after_request
#def after_request(response):
#    db_session.remove()
#    return response


@users_page.route('/_login', methods=['POST'])
def login_with_post():
    """Authenticate as a user.

    **Example request**:

    .. sourcecode:: http

       POST /users/login HTTP/1.1
       Host: csdms.colorado.edu
       Content-Type: application/json

       {
         "username": "joe_blow",
         "password": "dragon"
       }

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
         "_type": "user",
         "id": 123,
         "href": "/users/123",
         "username": "joe_blow",
         "links": [
           {
             "rel": "collection/tags",
             "href": "/users/123/tags"
           },
           {
            "rel": "collection/models",
            "href": "/users/123/models"
           }
         ]
       }

    :reqheader Content-Type: application/json
    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 400: bad json
    :statuscode 401: authentication error
    """
    data = deserialize_request(request, fields=['username', 'password'])
    try:
        u, p = data['username'], data['password']
    except KeyError:
        raise InvalidJsonError()

    if users.authenticate(u, p):
        return users.first(username=u).jsonify()
    else:
        raise AuthenticationError()


@users_page.route('/_login', methods=['GET'])
def login_with_get():
    """Authenticate as a user.

    **Example request**:

    .. sourcecode:: http

       GET /users/login HTTP/1.1
       Host: csdms.colorado.edu
       Content-Type: application/json
       Authorization: Basic ZXJpYzoxMjM0NTY=

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
         "_type": "user",
         "id": 123,
         "href": "/users/123",
         "username": "joe_blow",
         "links": [
           {
             "rel": "collection/tags",
             "href": "/users/123/tags"
           },
           {
            "rel": "collection/models",
            "href": "/users/123/models"
           }
         ]
       }

    .. sourcecode:: bash

        > curl -u joe_blow:dragon http://rcem.colorado.edu/users/login
    """

    auth = request.authorization

    if auth is not None:
        username, password = auth.username, auth.password
    else:
        username = request.args.get('username', None)
        password = request.args.get('password', None)

        if not username:
            raise MissingFieldError('credentials', 'username')
        if not password:
            raise MissingFieldError('credentials', 'password')

    if users.authenticate(username, password):
        login_user(User(username), remember=True)
        return users.first(username=username).jsonify()

    raise AuthenticationError()


@users_page.route('/_logout', methods=['GET'])
def _logout():
    """Log out the currently authenticated user.

    **Example request**:

    .. sourcecode:: http

       GET /users/logout HTTP/1.1
       Host: csdms.colorado.edu
    """
    logout_user()
    return "", 204


@users_page.route('/show', methods=['GET'])
def show():
    """Get a list of user instances for all users.

    **Example request**:

    .. sourcecode:: http

       GET /users HTTP/1.1
       Host: csdms.colorado.edu
       Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       [{
         "_type": "user",
         "id": 123,
         "href": "/users/123",
         "username": "joe_blow",
         "links": [
           {
             "rel": "collection/tags",
             "href": "/users/123/tags"
           },
           {
            "rel": "collection/models",
            "href": "/users/123/models"
           }
         ]
       }]


    :query sort: name of field by which results are sorted
    :query order: sort result in ascending or descending order (*asc* or
                  *desc*).
    :reqheader Content-Type: application/json
    :resheader Content-Type: application/json
    :statuscode 200: no error
    :statuscode 400: bad json
    :statuscode 401: authentication error
    """
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    return users.jsonify_collection(users.all(sort=sort, order=order))


@users_page.route('/', methods=['POST'])
def create():
    """Create a new user.

    **Example request**:

    .. sourcecode:: http

       POST /users HTTP/1.1
       Host: csdms.colorado.edu
       Content-Type: application/json

       {
         "username": "joe_blow",
         "password": "dragon"
       }

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
         "_type": "user",
         "id": 123,
         "href": "/users/123",
         "username": "joe_blow",
         "links": [
           {
             "rel": "collection/tags",
             "href": "/users/123/tags"
           },
           {
            "rel": "collection/models",
            "href": "/users/123/models"
           }
         ]
       }

    :reqheader Content-Type: application/json
    :resheader Content-Type: application/json
    :statuscode 200: no error
    :statuscode 400: bad JSON
    :statuscode 422: user already exists
    """
    data = deserialize_request(request, fields=['username', 'password'])

    user = users.first(username=data['username'])
    if user:
        raise AlreadyExistsError("User", "username")
    else:
        user = users.create(data['username'], data['password'])
    return user.jsonify()


@users_page.route('/search')
def search():
    """Search for users.
    """
    username = request.args.get('username', None)
    contains = request.args.get('contains', None)

    if contains is not None:
        names = users.contains(contains)
    elif username is not None:
        names = users.find(username=username)
    else:
        names = users.all()

    return as_collection([user.to_resource() for user in names])


@users_page.route('/<int:id>', methods=['GET'])
def user(id):
    """Get a user instance.

    **Example request**:

    .. sourcecode:: http

       GET /users/123 HTTP/1.1
       Host: csdms.colorado.edu
       Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
         "_type": "user",
         "id": 123,
         "href": "/users/123",
         "username": "joe_blow",
         "links": [
           {
             "rel": "collection/tags",
             "href": "/users/123/tags"
           },
           {
            "rel": "collection/models",
            "href": "/users/123/models"
           }
         ]
       }

    :reqheader Content-Type: application/json
    :resheader Content-Type: application/json
    :statuscode 200: no error
    :statuscode 404: no user
    """
    return users.get_or_404(id).jsonify()


@users_page.route('/<int:id>', methods=['DELETE'])
def delete(id):
    """Delete a user.

    **Example request**:

    .. sourcecode:: http

       DELETE /users/123 HTTP/1.1
       Host: csdms.colorado.edu
       Content-Type: application/json

       { "password": "dragon" }
    """
    u = users.get_or_404(id)
    data = deserialize_request(request, fields=['password'])

    if users.authenticate(u.username, data['password']):
        users.delete(u)
    else:
        raise AuthenticationError()

    return "", 204


@users_page.route('/<int:id>', methods=['PATCH'])
def change_password(id):
    """Change the password for a user.

    **Example request**:

    .. sourcecode:: http

       PATCH /users/123 HTTP/1.1
       Host: csdms.colorado.edu
       Content-Type: application/json

       {
         "old_password": "dragon",
         "new_password": "mississippi"
       }
    """
    data = deserialize_request(request, require=['password'])

    u = users.get_or_404(id)

    if not users.change_password(u.username, data['password'],
                                 data['password']):
        raise AuthenticationError()

    return u.jsonify()


@users_page.route('/<int:id>/tags')
def tags(id):
    """Get the tags owned by a user.
    """
    user = users.get_or_404(id)
    return users.jsonify_collection(user.tags)


@users_page.route('/<int:id>/models')
def models(id):
    """Get the models owned by a user.
    """
    user = users.get_or_404(id)
    return users.jsonify_collection(user.models)


@users_page.route('/<int:id>/models/search')
def search_models(id):
    """Search models owned by a user.

    **Example request**:

    .. sourcecode:: http

       GET /users/123/models/search HTTP/1.1
       Host: csdms.colorado.edu
       Content-Type: application/json

    :query sort: name of field by which results are sorted (*tag_id* or *tag*)
    :query order: sort result in ascending or descending order (*asc* or
                  *desc*).
    :reqheader Content-Type: application/json
    :resheader Content-Type: application/json
    :statuscode 200: no error
    :statuscode 400: bad json
    :statuscode 401: authentication error
    """
    search = {}
    if 'tag_id' in request.args:
        search['id'] = request.args['tag_id']
    if 'tag' in request.args:
        search['tag'] = request.args['tag']

    models = users.get_or_404(id).models
    if search:
        models = models.filter(Model.tags.any(**search))

    return users.jsonify_collection(models)


@users_page.route('/whoami')
def whoami():
    """Returns the name of the currently authenticated user.
    """
    #user = users.first(username=current_user.get_id())
    user = users.first(username=get_current_user(cached=False))
    if user:
        return user.jsonify()
        #return user, 200
    else:
        return '', 204
