#!/usr/bin/env python

from distutils.core import setup

setup(name='registration',
      version='0.1',
      description='HackNC Registration app',
      author='Brandon Davis',
      author_email='bdavis@redspin.net',
      url='https://hacknc.com',
      install_requires=[
        'flask==0.11.1',
        'requests==2.10.0',
        'requests_oauthlib==0.6.2',
        'flask-sqlalchemy==2.1',
        'flask_login==0.3.2',
        'uwsgi==2.0.13.1',
        'psycopg2==2.6.2',
        'flask-cors'
      ],
)