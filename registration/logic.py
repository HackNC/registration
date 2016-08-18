import datetime

from . import models
from . import utilities
from . import settings

def cut_batch(mock=True):
    """
    Moves all open applications into the batch pending state.
    :param mock: Simply show what the output would be, but don't modify the object model.  (Dry run)
    """

    all_users = models.HackerUser.query

    for user in all_users:

        if user.visible_status in ['o']:

            user.admin_update({
                "visible_status": settings.BATCH_PENDING_STATUS,
                "pending_status": settings.NULL_PENDING_STATUS,
            })

def process_pending(mock=True):
    """
    Define logic to process pending-state applications.
    :param mock: Simply show what the output would be, but don't modify the object model.  (Dry run)
    """
    all_users = models.HackerUser.query

    for user in all_users:

        # If we are moving from a non-accepted state to an accepted state
        if (user.visible_status in ['p', 'w', 'r'] 
            and user.pending_status in  ['a', 't', 'n']):
            
            user.admin_update({
                "visible_status": user.pending_status,
                "pending_status": settings.NULL_PENDING_STATUS,
                "rsvp": False,
                "rsvp_by": datetime.datetime.utcnow() + datetime.timedelta(days=settings.DAYS_TO_RSVP),
            })  # Update the user
            utilities.send_state_changed_email(user)  # Notify user of change

        # If we are moving from a non-accepted to another non-accepted state
        elif (user.visible_status in ['p', 'w', 'r']
            and user.pending_status in ['w', 'r']
            and user.pending_status != user.visible_status):

            user.admin_update({
                "visible_status": user.pending_status,
                "pending_status": settings.NULL_PENDING_STATUS,
            })
            utilities.send_state_changed_email(user)

def show_rsvp_form(user):
    """
    Given a user, decide whether or not to show them the RSVP form
    returns T/F
    """
    assert(isinstance(user, models.HackerUser))

    if (user.rsvp == False 
        and status in ['a', 't', 'n']
        and datetime.datetime.utcnow() < user.rsvp_by):
        
        return True

    return False