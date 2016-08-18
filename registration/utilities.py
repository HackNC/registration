from . import settings


# Any simple static helpers go in here.

def build_auth_url():
    return settings.MYMLH['auth_url'].format(
        client_id=settings.MYMLH['app_id'],
        callback_uri=settings.MYMLH['redirect_uri']
    )

def get_by_code(code, StatusCodes):
    if code in StatusCodes.keys():
        return StatusCodes[code]
    else:
        return StatusCodes['x']

def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def send_state_changed_email(user):
    pass