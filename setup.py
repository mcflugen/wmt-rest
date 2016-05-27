#!/usr/bin/env python

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup, find_packages
from setuptools.command.install import install

from wmt import __version__


setup(name='wmt',
      version=__version__,
      description='RESTful API for the Web Modeling Tool',
      author='Eric Hutton',
      author_email='eric.hutton@colorado.edu',
      url=' http://csdms.colorado.edu/',
      install_requires=['flask', 'flask-sqlalchemy', 'flask-testing',
                        'flask-login', 'pyyaml',
                        'passlib', 'standard_names', 'paramiko'],
      packages=find_packages(),
      long_description="Create, save, edit, run collections of connected components.",
      license="Public domain",
      platforms=["any"],
      scripts=['scripts/wsgi.py', ],
     )
