#!/usr/bin/env python

from distutils.core import setup

setup(name='registration',
      version='0.1',
      description='HackNC Registration app',
      author='Brandon Davis, Peter Andringa',
      author_email='bdavis@redspin.net, peter@andrin.ga',
      url='https://hacknc.com',
      install_requires=[
        'Flask==0.11.1',
        'Flask-Cors==2.1.2',
        'Flask-Sqlalchemy==2.1',
        'Flask-Login==0.3.2',
        'requests==2.10.0',
        'requests-oauthlib==0.6.2',
        'uwsgi==2.0.13.1',
        'psycopg2==2.6.2',
        'python-dateutil==2.5.3',
        'sparkpost==1.2.0',
        'python-dateutil'
      ],
)