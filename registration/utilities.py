# Any simple static helpers go in here.

def get_by_code(code, StatusCodes):
    if code in StatusCodes.keys():
        return StatusCodes[code]
    else:
        return StatusCodes['u']

def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z