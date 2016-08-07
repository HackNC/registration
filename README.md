# registration
A flask app for HackNC registration using MyMLH for auth.

# Requirements

use aptto install the following

```
sudo apt-get install python3 python3-dev python-dev libpq-dev virtualenv postgresql nginx
```

# Development 

clone the code and checkout a branch

Create a virtual environment: `virtualenv -p python3 .`

Activate `source bin/activate`

run a development install `pip install -e .`

You'll need to ask for a copy of settings.py to drop in the main registration directory.  It contains all our secrets!!  

You'll also need to configure a postgresql user to do password login `pg_hba.conf` and create a database for that user.  `CREATE ROLE {role} WITH PASSWORD {passwd} CREATEDB;`

After the database creation, you'll need to build the schema.  `python registration.py migrate debug` will do this for you.

To run in prod, it's highly recommended that you sit flask behind nginx using wsgi. 

`wsgi --ini registration.ini` will start the server.

# Usage

This project contains the following endpoints:

```
/
    GET - will cause a redirect to MLH auth based on settings.py

/login
    GET - should be registered as the MLH callback.  Never call this manually.

/logout
    GET - logs the user out

/dashboard
    GET - returns the user's current details
    POST - specify the fields to update in a form.  MLH-related fields should update on my.mlh.io - changes will reflect
```