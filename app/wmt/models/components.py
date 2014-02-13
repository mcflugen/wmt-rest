import json

from ..palette import PALETTE


class Error(Exception):
    pass


class IdError(Error):
    def __init__(self, id):
        self._id = id

    def __str__(self):
        return str(self._id)


def get_components():
    return PALETTE.values()


def get_component_names(sort=False):
    names = list(PALETTE.keys())
    if sort:
        names.sort()
    return names


def get_component(name):
    try:
        return PALETTE[name]
    except KeyError:
        raise IdError(name)