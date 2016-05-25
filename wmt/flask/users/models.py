from flask import Response, url_for

from ..core import db, JsonMixin


class UserJsonSerializer(JsonMixin):
    __public_fields__ = set(['href', 'id', 'username', 'openid'])


class User(UserJsonSerializer, db.Model):
    __tablename__ = 'users'
    __bind_key__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256))
    #email = db.Column(db.String(256), unique=True)
    openid = db.Column(db.String(2048), unique=True)

    password = db.Column(db.Text)
    tags = db.relationship('Tag', backref='owned_by', lazy='dynamic')
    models = db.relationship('Model', backref='owned_by', lazy='dynamic')
    sims = db.relationship('Sim', backref='user', lazy='dynamic')

    @property
    def href(self):
        return url_for('.user', id=self.id)

    @property
    def object_links(self):
        links = []
        for tag in self.tags:
            links.append(dict(rel='resource/tags',
                              href=url_for('tags.tag', id=tag.id)))
        for model in self.models:
            links.append(dict(rel='resource/models',
                              href=url_for('models.model', id=model.id)))
        return links

    #def __init__(self, username, password):
    def __init__(self, username, openid):
        self.username = username
        #self.email = email
        self.openid = openid
        #self.password = password

    def __repr__(self):
        return '<User %r>' % self.username
