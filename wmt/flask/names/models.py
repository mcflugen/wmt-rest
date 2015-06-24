from flask import url_for

from standard_names import StandardName
from ..core import db, JsonMixin


provides_names = db.Table(
    'provides_names', db.metadata,
    db.Column('component_id', db.Integer, db.ForeignKey('components.id')),
    db.Column('name_id', db.Integer, db.ForeignKey('names.id')),
    info={'bind_key': 'names'})

uses_names = db.Table(
    'uses_names', db.metadata,
    db.Column('component_id', db.Integer, db.ForeignKey('components.id')),
    db.Column('name_id', db.Integer, db.ForeignKey('names.id')),
    info={'bind_key': 'names'})


class NameJsonSerializer(JsonMixin):
    __public_fields__ = set(['href', 'id', 'name', 'object', 'quantity',
                             'operators'])


class Name(NameJsonSerializer, db.Model):
    __tablename__ = 'names'
    __bind_key__ = 'names'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(2048), unique=True)

    provided_by = db.relationship('Component', secondary=provides_names,
                                 backref='provided_by', lazy='dynamic')
    used_by = db.relationship(
        'Component', secondary=uses_names,
        backref='used_by', lazy='dynamic')

    @property
    def href(self):
        return url_for('names.name', id=self.id)

    @property
    def object_links(self):
        links = []
        for name in self.provided_by:
            links.append(
                dict(rel='resource/providedby',
                     href=url_for('components.component', id=name.id)))
        for name in self.used_by:
            links.append(
                dict(rel='resource/usedby',
                     href=url_for('components.component', id=name.id)))
        return links

    @property
    def object(self):
        return StandardName(self.name).object

    @property
    def quantity(self):
        return StandardName(self.name).quantity

    @property
    def operators(self):
        return StandardName(self.name).operators

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Name %r>' % self.name
