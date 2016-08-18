# Usage: import this from wherever you like, but be aware that
# this code is not part of the registration app, and not required to function.  
# It is, rather, more like runserver.py - the user implementation of registration.

from registration import triggers, settings  # I like to keep all my secrets in settings.py
from sparkpost import SparkPost  # Import any other non-essential libraries here.
import requests
import json

sp = SparkPost(settings.SPARKPOST['secret_key'])

# Trigger example.  When an new user is created, print them out to console.
@triggers.new_user
def say_hello(user):
    """
    This is an example of a callback.  
    Decorate it with trigger.new_user to get called when new users are created.

    :param user: An instance of models.User
    :returns: None
    """
    print('NEW USER: ' + user.first_name)

# Send email.  When a new user is created, send them a friendly welcome email
@triggers.new_user
def send_welcome(user):
    response = sp.transmission.send(
        recipients=[ user.email ],
        track_opens=True,
        track_clicks=True,
        template='signup-confirm',
        substitution_data={
            'name': user.first_name
        }
    )
    print(response)

# Feed the new user into slack
@triggers.new_user
def send_slack(user):
    data = {"text": user.first_name + " " + user.last_name + " (" + user.email + ") registered for HackNC.\n<https://my.hacknc.com/admin/user/" + user.email + "| View Application>"}
    r = requests.post(settings.SLACK['webhook_url'],data=json.dumps(data))
    print("Slack Reply: " + r.text)
