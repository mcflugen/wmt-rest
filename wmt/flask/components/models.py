import os

from flask import current_app, abort

from ...utils.db import load_palette
from ..core import db

import local_settings


class Component(object):
    def __init__(self):
        self.palette = load_palette(
            os.path.join(local_settings.WMT_DATABASE_DIR, 'components'))

    def all(self):
        return self.palette.values()

    def get(self, name):
        return self.palette.get(name, None)

    def get_or_404(self, name):
        return self.get(name) or abort(404)

    def get_names(self, sort=False):
        names = list(self.palette.keys())
        if sort:
            names.sort()
        return names

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


