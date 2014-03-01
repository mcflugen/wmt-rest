import os
import urlparse
import urllib2
import tarfile


PICKUP_URL = 'http://csdms.colorado.edu/pub/users/wmt/'
CHUNK_SIZE_IN_BYTES = 10240


def get_filename_from_header(header):
    try:
        disposition = headers['content-disposition']
    except KeyError:
        raise

    for attr in disposition.split(';'):
        if attr.strip().startswith('filename'):
            dest_name = attr[attr.index('=') + 1:].strip()
            break

    return dest_name


def download_file(url):
    resp = requests.get(url, stream=True)

    try:
        dest_name = get_filename_from_header(resp.headers)
    except KeyError:
        dest_name = os.path.basename(url)

    with open(dest_name, 'wb') as fp:
        for chunk in resp.iter_content():
            if chunk: # filter out keep-alive new chunks
                fp.write(chunk)
                fp.flush()

    return dest_name


def download_run_tarball(uuid):
    import requests

    url = os.path.join('http://csdms.colorado.edu/wmt/run/download', uuid)
    resp = requests.get(url, stream=True)

    dest_name = uuid + '.tar.gz'
    with open(dest_name, 'wb') as fp:
        for chunk in resp.iter_content():
            if chunk: # filter out keep-alive new chunks
                fp.write(chunk)
                fp.flush()

    return dest_name

def upload_run_tarball(uuid):
    import requests
    import requests_toolbelt

    url = os.path.join('http://csdms.colorado.edu/wmt/run/upload', uuid)
    with open(uuid + '.tar.gz', 'r') as fp:
        m = MultipartEncoder(fields={'file': (uuid + '.tar.gz', fp, 'application/x.gzip')})
        resp = requests.post(url, data=m, headers={'Content-Type': m.content_type})

    return resp


def download_chunks(url):
    try:
        resp = urllib2.urlopen(url)
    except urllib2.HTTPError:
        raise

    print resp.info().getheader('Transfer-Encoding')
    dest_name = os.path.basename(url)

    with open(dest_name, 'w') as dest_fp:
        while 1:
            chunk_size = int(resp.readline())
            if chunk_size == 0:
                break
            chunk = resp.read(chunk_size)
            dest_fp.write(chunk)
            resp.read(2)

    return os.path.abspath(dest_name)


class WmtTask(object):
    def __init__(self, id):
        self._id = id
        self._wmt_dir = os.path.abspath('.wmt')
        self._task_dir = os.path.join(self._wmt_dir, id)

    @property
    def id(self):
        return self._id

    @property
    def task_dir(self):
        return self._task_dir

    def setup(self):
        try:
            os.makedirs(self.task_dir)
        except os.error:
            pass

        os.chdir(self._wmt_dir)

        dest = download_run_tarball(self.id)

        with tarfile.open(dest) as tar:
            tar.extractall()

        os.chdir(self.task_dir)

    def run(self):
        os.chdir(self.task_dir)


    def teardown(self):
        os.chdir(self._wmt_dir)

        with tarfile.open(self.id + '.tar.gz') as tar:
            tar.add(self.id)

        upload_run_tarball(self.id)


    def execute(self):
        self.setup()
        self.run()
        self.teardown()



def launch(id):
    task = WmtTask(id)
    task.execute()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('id', help='Run ID')
    args = parser.parse_args()

    launch(args.id)


if __name__ == '__main__':
    main()
