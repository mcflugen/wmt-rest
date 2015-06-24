import os

from flask import current_app, abort, url_for

from ...utils.db import load_palette
from ..core import db, JsonMixin

import local_settings


class ComponentJsonSerializer(JsonMixin):
    __public_fields__ = set(['href', 'id', 'name'])


class Component(ComponentJsonSerializer, db.Model):
    __tablename__ = 'components'
    __bind_key__ = 'names'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    #author = db.Column(db.String(128))
    #doi = db.Column(db.String(128))
    #summary = db.Column(db.String(2048))
    #url = db.Column(db.String(128))
    #version = db.Column(db.String(128))
    #uses = db.relationship('Name', secondary='names', backref='names',
    #                       lazy='dynamic')
    provides = db.relationship('Name', secondary='provides_names',
                               backref='provides_names', lazy='dynamic')
    uses = db.relationship('Name', secondary='uses_names',
                           backref='uses_names', lazy='dynamic')

    #def __init__(self):
    #    self.palette = load_palette(
    #        os.path.join(local_settings.WMT_DATABASE_DIR, 'components'))

    #def all(self):
    #    return self.palette.values()

    #def get(self, name):
    #    return self.palette.get(name, None)

    #def get_or_404(self, name):
    #    return self.get(name) or abort(404)

    #def get_names(self, sort=False):
    #    names = list(self.palette.keys())
    #    if sort:
    #        names.sort()
    #    return names

    @property
    def href(self):
        return url_for('components.component', id=self.id)

    @property
    def object_links(self):
        links = []
        for name in self.provides:
            links.append(dict(rel='resource/provides',
                              href=url_for('names.name', id=name.id)))
        for name in self.uses:
            links.append(dict(rel='resource/uses',
                              href=url_for('names.name', id=name.id)))
        return links

    #@property
    #def link_objects(self):
    #    return {
    #        'user': { 'href': url_for('users.user', id=self.owned_by.id)},
    #    }

    def input(self, name):
        filenames = self.get(name)['files']

        files = {}
        for (fid, filename) in enumerate(filenames):
            files[filename] = _read_input_file(name, filename)

        return files


def _read_input_file(name, filename):
    input_file_dir = os.path.join(local_settings.WMT_DATABASE_DIR,
                                  'components', name, 'files')
    path_to_file = os.path.join(input_file_dir, filename)
    with open(path_to_file, 'r') as file:
        contents = file.read()
    return contents


