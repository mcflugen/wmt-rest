import os
from datetime import datetime
from uuid import uuid4
import json
from distutils.dir_util import mkpath

from flask import current_app, url_for

from ..core import db, JsonMixin


class FileJsonSerializer(JsonMixin):
    __hidden_fields__ = set()
    __public_fields__ = set(['id', 'name', 'contents', 'href'])


class File(FileJsonSerializer, db.Model):
    __tablename__ = 'files'
    __bind_key__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer,
                             db.ForeignKey('components.id',
                                           info={'bind_key': 'names'}))
    name = db.Column(db.String(2048))
    contents = db.Column(db.Text)

    @property
    def href(self):
        return url_for('files.file', id=self.id)

    @property
    def link_objects(self):
        if self.component_id:
            return {
                'component': {'href': url_for('components.component',
                                              id=self.component_id)},
            }
        else:
            return {}

    def __repr__(self):
        return '<File %r>' % self.name
