# registration
A flask app for HackNC registration using MyMLH for auth.

# What is this?

Registration is a [Flask app](http://flask.pocoo.org/) built to extend the MyMLH object model.  Your hackathon users will "Sign in with MLH" and then get redirected back to the Registration dashboard.  It maintains the extended object model in a postgres database.  It also manages application status, and changes the view as applications are open, accepted, rejected, and checked in.

This enables you to do things like:
* Not worry about logins / password security
* Accept resumes
* Ask additional questions and collect info no included in the MLH form.
* ( In development) Trigger custom python callbacks for.
  * New user creation
  * User info updates
* Manage registrations with an admin panel.
* Provide dashboard for acceptances
* Provide dasbboard for check-in

# MyMLH Setup.

1. [Create a new MLH app](https://my.mlh.io/oauth/applications) and take note of your client_id and secret.
2. Set an application callback to my_server.domain/login, where my_server.domain points to the root '/' for this app.

# Requirements

You'll need a public-facing host to run this app.  The developers here like DigitalOcean, but you could host anywhere!  The remainder of this README assumes your server is running a modern version of Ubuntu.

use apt to install the following packages:

```
sudo apt-get install python3 python3-dev python-dev libpq-dev virtualenv postgresql nginx
```

# Database setup

1. after installing postgres, log in as the postgres user. `sudo su postgres && psql`
2. Create a user for the application. `CREATE ROLE registration WITH PASSWORD {passwd} CREATEDB;`
3. Create a database for that role. `CREATE DATBASE registration OWNER registration`;
4. Edit `/etc/postgres/{version}/main/pg_hba.conf` : add the line `local   all   registration   md5`
5. Restart postgres.  `sudo service postgresql restart`

# Development 

1. clone the code and checkout a branch.  It's a good idea to put apps in `/opt/<app_name/`
2. Create a virtual environment: `virtualenv -p python3 .`
3. Activate `source bin/activate`
4. run a development install `pip install -e .`
5. You'll need to ask for a copy of settings.py to drop in the main registration directory.  It contains all our secrets!!  
6. After the database creation, you'll need to build the schema.  `python registration.py migrate debug` will do this for you.

To run in prod, it's highly recommended that you sit flask behind nginx using wsgi. 

`uwsgi --ini registration.ini` will start the server.  Do not run this as root.

`python registration.py debug` will start a single thread in debug mode.  *DEBUG MODE IS NOT SAFE FOR PRODUCTION*

# Modification

You'll need to read and modify the code and object model in [models.py](models.py).  

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

/admin
    GET - returns admin interface

/admin/update/{user_id}
    POST - adminstrative endpoint to set any user field
```

To give a user administrative privileges, log into a postgres prompt and run: `UPDATE public."user" SET is_admin = true WHERE email = '{user email}';`

# Contributing

This project is chill.  Fork it - code it - pull request it with docs.  No fuss, no muss.