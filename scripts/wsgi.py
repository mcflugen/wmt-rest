#! /usr/bin/env python
from os import path
from flask.ext.openid import OpenID
from openid.extensions import pape

from wmt.flask import create_app

import local_settings


application = create_app(settings_override=local_settings,
                         wmt_root_path=path.abspath(path.dirname(__file__)))
oid = OpenID(application, safe_roots=[], extension_responses=[pape.Response])


#if __name__ == "__main__":
#    from os import path
#
#    create_app(wmt_root_path=path.abspath(path.dirname(__file__))).run()
