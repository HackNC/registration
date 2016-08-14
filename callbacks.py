import os

from registration import triggers, settings
from sparkpost import SparkPost

# Example
@triggers.new_user
def say_hello(user):
    """
    This is an example of a callback.  
    Decorate it with trigger.new_user to get called when new users are created.

    :param: user: An instance of models.User
    :returns: None
    """
    print('NEW USER: ' + user.first_name)

# Send email
sp = SparkPost(settings.SPARKPOST['secret_key'])

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