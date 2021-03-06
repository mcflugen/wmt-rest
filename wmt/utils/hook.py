import os


class Error(Exception):
    pass


class FileNotFoundError(Error):
    def __init__(self, filename, paths):
        self._filename = filename
        self._paths = paths

    def __str__(self):
        message = [
            '%s: file not found' % self._filename,
            'search paths:',
        ] + self._paths
        return os.linesep.join(message)

def find_file(filename, paths=['.', ]):
    for path in paths:
        path_to_file = os.path.join(path, filename)
        if os.path.isfile(path_to_file):
            return path_to_file
    return None


def find_file_in_search_path(filename, envvar):
    paths = os.environ.get(envvar, os.getcwd()).split(os.pathsep)
    found = find_file(filename, paths=paths)
    if found:
        return found
    else:
        raise FileNotFoundError(filename, paths)


def find_simulation_input_file(filename):
    return find_file_in_search_path(filename, 'WMT_INPUT_FILE_PATH')
