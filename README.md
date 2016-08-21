# registration

A flask app for HackNC registration using MyMLH for auth.

# What is this?

Registration is a [Flask app](http://flask.pocoo.org/) built to extend the MyMLH object model.  Your hackathon users will "Sign in with MLH" and then get redirected back to the Registration dashboard.  It maintains the extended object model in a postgres database.  It also manages application status, and changes the view as applications are open, accepted, rejected, and checked in.

This enables you to do things like:
* Not worry about logins / password security / account recovery
* Accept resumes
* Ask additional questions and collect info not included in the MLH form.
* Trigger any python callbacks for:
  * New user creation
  * User info updates
* Trigger transactional email and slack notifications (optional)
* Manage applicants with an admin panel.
* Provide dashboard for acceptances and check-ins

# Setup

## MyMLH Setup.

1. [Create a new MLH app](https://my.mlh.io/oauth/applications) and take note of your client_id and secret.
2. Set an application callback to my_server.domain/login, where my_server.domain points to the root '/' for this app.

## System Requirements

You'll need a public-facing host to run this app.  The developers here like DigitalOcean, but you could host anywhere!  The remainder of this README assumes your server is running a modern version of Ubuntu.

use apt to install the following packages:

```
sudo apt-get install python3 python3-dev python-dev libpq-dev virtualenv postgresql nginx
```

## Database Setup

1. after installing postgres, log in as the postgres user. `sudo su postgres && psql`
2. Create a user for the application. `CREATE ROLE registration WITH PASSWORD {passwd} CREATEDB;`
3. Create a database for that role. `CREATE DATBASE registration OWNER registration`;
4. Edit `/etc/postgres/{version}/main/pg_hba.conf` : add the line `local   all   registration   md5`
5. Restart postgres.  `sudo service postgresql restart`

## Environment Setup and Development

1. clone the code and checkout a branch.  It's a good idea to put apps in `/opt/<app_name/`
2. Create a virtual environment: `virtualenv -p python3 .`
3. Activate `source bin/activate`
4. run a development install `pip install -e .`
5. Move settings_example.py to settings.py and fill out all the fields 
6. After the database creation, you'll need to build the schema.  `python registration.py migrate` will do this for you.

To run in prod, it's highly recommended that you sit flask behind nginx using uwsgi. 

`uwsgi --ini registration.ini` will start the server.  Do not run this as root.

`python registration.py debug` will start a single thread in debug mode.  *DEBUG MODE IS NOT SAFE FOR PRODUCTION*

# Callbacks

HackNC uses a couple of callback which require some other api keys/setup.

1) SparkPost API: sparkpost does transactional email.  You will need to set up an account, generate an API key that can WRITE transmissions and read templates, and create a template.  you can send it the "name" substitution data.

2) Slack Webhooks: Create a new custom slack integration, pick the channel, and paste the url into settings.py

# Custom Modification

You'll need to read and modify the code in these files to create a custom registration app:
* [models.py](registration/models.py) - Modify User, HackerUser to reflect the desired schema
* [forms.py](registration/forms.py) - modify the forms.  
* [views.py](registration/hacker/views.py) - Example of a views file.  You can create new micro-apps in their own submodules by following the design pattern in registration.hacker

# Usage

This system exposes the following endpoints:

```
/
    GET - Will render the index page if the requesting user does not have an active session.
        - else, will redirect to settings.DEFAULT_VIEW 

/login
    GET - should be registered as the MLH callback.  Never call this on your own.

/logout
    GET - logs the user out.  Redirects to /

/dashboard
    GET - returns the user's current status and team.

/apply
    GET - renders the current user's application state.
    POST - update the current user's application state.

/api/me
    GET - gets the logged in user's JSON representation.

/admin
    GET - returns admin interface

/admin/user/{user_email}
    GET - gets any specified user's JSON respresentation.
    POST - adminstrative endpoint to set any user field, then redirect back to /admin
```

To give a user administrative privileges, log into a postgres prompt and run: 

`UPDATE public."user" SET is_admin = true WHERE email = '{user email}';`

# Contributing

This project is chill.  Fork it - code it - pull request it with docs.  No fuss, no muss.