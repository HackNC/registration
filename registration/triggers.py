from . import models

def new_user(callback):

    def trigger_wrapper(user):
        """
        New user trigger - can decorate later if we need to
        :param user: a user object
        """
        return callback(user)

    # Register the callback
    models.User.register_create_callback(trigger_wrapper)
    return trigger_wrapper

def update_user(callback):

    def trigger_wrapper(user):
        """
        User update trigger - can decorate later
        :param user: a user object
        """
        return callback(user)

    # Register the callback
    models.User.register_update_callback(trigger_wrapper)
    return trigger_wrapper