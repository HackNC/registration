import collections

# The status codes and their meanings
# These are the statuses that a user account can be in
# Here's how HackNC does it:
# open > aaccepted / rejected / travel +accepted / notravel +accepted / waitlisted
# waitlisted > accepted / travel +accepted / notravel +accepted
# accepted / travel +accepted / notravel +accepted > checked-in
StatusCodes = {
    'o': {
        # The database code
        "code": "o",
        # The name to show the user
        "friendly_name": "Open", 
        # Some help text about what it means
        "help_text": "Applications are still open!  Make any changes you want - we'll submit for you when they close.",
        # Whether this state allows the user to edit their application
        "editable_state": True
    },
    'p': {
        "code" : "p",
        "friendly_name": "Pending",
        "help_text": "Your application has been submitted!  We're still reviewing, so check back often!",
        "editable_state": False
    },
    'a': {    
        "code": "a",
        "friendly_name": "Accepted",
        "help_text": "Congrats - You're accepted!  Keep an eye on your email for further actions.",
        "editable_state": False
    },
    'r': {
        "code": "r",
        "friendly_name": "Not Accepted",
        "help_text": "Unfortunately, we couldn't reserve a spot for you this year.  Don't be discouraged - there were a ton of hackers that wanted in.  If you think there may have been a mistake, send mail to hello@hacknc.com",
        "editable_state": False
    },
    'w': {
        "code": "w",
        "friendly_name": "Waitlisted",
        "help_text": "Sit tight!  We're trying to find you a spot.  Check back often!",
        "editable_state": False
    },
    't': {
        "code": "t",
        "friendly_name": "Accepted with Travel",
        "help_text": "Congrats - You're accepted with a travel reimbursement!  Keep an eye on your email for further actions.  Questions about travel can be directed to travel@hacknc.com",
        "editable_state": False
    },
    'n': {
        "code": "n",
        "friendly_name": "Accepted without Travel",
        "help_text": "Congrats - You're accepted!  Unfortunately, we can't compensate you for travel.  If you have any questions, shoot us an email at hello@hacknc.com",
        "editable_state": False
    },
    'x': {
        "code": "x",
        "friendly_name": "Null",
        "help_text": "You've been marked with a status code we don't recognize.  It's probably temporary, but if you have any questions, email hello@hacknc.com :)",
        "editable_state": False
    }
}

# Master list of form items.  Can span many types of users.
master = {
    "what_to_learn": {
        # The field name to shwo the user
        "friendly_name": "What do you want to learn?",
        # Some help text to explain what they should put
        "help_text": "Whether it be virtual reality, the internet of things, or how to scrape together your first webpage, let us know what you're interested in learning!",
        # What sort of form is this?
        "formtype": "textarea",
        # Is the field editable regardless of registration_status?
        "always": False,
        # Is the field required?
        "required": False,
        # Is the field editable at all?
        "editable": True,
        # Max length in chars.  -1 = infinite
        "max_length": -1,
    },
    "background": {
        "friendly_name": "Your Background",
        "help_text": "Tell us a little more about you!  How'd you get into tech?",
        "formtype": "textarea",
        "max_length": -1,
        "always": False,
        "required": False,
        "editable": True,
        "pattern": "^.+$"
    },
    "github": {
        "friendly_name" : "GitHub URL",
        "help_text" : "A link to your github profile",
        "formtype": "text",
        "max_length": 128,
        "always": False,
        "required": False,
        "editable": True,
        "pattern": "^([Hh][Tt][Tt][Pp][Ss]?:\/\/)?[Gg][Ii][Tt][Hh][Uu][Bb]\.com\/[\w]+$"
    },
    "website": {
        "friendly_name" : "Personal URL",
        "help_text" : "Could be your website, or a link to something else you're proud of.",
        "formtype": "text",
        "max_length": 128,
        "always": False,
        "required": False,
        "editable": True,
        "pattern": "^([Hh][Tt][Tt][Pp][Ss]?:\/\/)?([\dA-Za-z\.-]+)\.([A-Za-z\.]{2,6})([\/\w \.-]*)*\/?$"
    },
    "mac_address": {
        "friendly_name" : "MAC Address",
        "help_text" : "The MAC accress of your laptop's wireless card.  We need this to connect you to our WIFI.",
        "formtype": "text",
        "always": True,
        "max_length": 20,
        "required": False,
        "editable": True,
        "pattern": "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    },
    "team_name": {
        "friendly_name": "Team Name",
        "help_text": "Create a team by giving us a team name.  Your teammates can all add the same name and get grouped.  This won't affect your application - it's just for fun!",
        "formtype": "text",
        "always": True,
        "max_length": 32,
        "required": False,
        "editable": True,
        "pattern": "^\w+$"
    },
    "email": {
        "friendly_name": "Email",
        "help_text": "",
        "formtype": "email",
        "max_length": 128,
        "required": True,
        "editable": False,  # Never editable
        "always": False
    },
    "first_name": {
        "friendly_name": "First Name",
        "help_text": "",
        "formtype": "text",
        "max_length": 128,
        "required": True,
        "editable": True,
        "always": False
    },
    "last_name": {
        "friendly_name": "Last Name",
        "help_text": "",
        "formtype": "text",
        "max_length": 128,
        "required": True,
        "editable": True,
        "always": False
    },
    "gender": {
        "friendly_name": "Gender",
        "help_text": "",
        "formtype": "text",
        "max_length": 64,
        "required": False,
        "editable": True,
        "always": False
    },
    "graduation": {
        "friendly_name": "Graduation",
        "help_text": "",
        "formtype": "date",
        "max_length": -1,
        "required": False,
        "editable": True,
        "always": False
    },
    "major": {
        "friendly_name": "Major",
        "help_text": "",
        "formtype": "text",
        "max_length": 128,
        "required": False,
        "editable": True,
        "always": False
    },
    "phone_number": {
        "friendly_name": "Phone Number",
        "help_text": "",
        "formtype": "+tel",
        "max_length": 32,
        "required": False,
        "editable": True,
        "always": False
    },
    "school_name": {
        "friendly_name": "School",
        "help_text": "",
        "formtype": "text",
        "max_length": 256,
        "required": True,
        "editable": True,
        "always": False
    },
    "date_of_birth": {
        "friendly_name": "Date of Birth",
        "help_text": "",
        "formtype": "date",
        "max_length": -1,
        "required": True,
        "editable": True,
        "always": False
    },
    "shirt_size": {
        "friendly_name": "Shirt Size",
        "help_text": "",
        "formtype": "text",
        "max_length": 32,
        "required": True,
        "editable": True,
        "always": False
    }, 
    "special_needs": {
        "friendly_name": "Special Needs",
        "help_text": "",
        "formtype": "text",
        "max_length": -1,
        "required": False,
        "editable": True,
        "always": False
    },
    "dietary_restrictions": {
        "friendly_name": "Dietary Restrictions",
        "help_text": "",
        "formtype": "text",
        "max_length": -1,
        "required": False,
        "editable": True,
        "always": False,
    }
}

# The list of keys MLH is allowed to set - don't touch this
mlh_settable_keys = [
    "mlh_id", 
    "created_at", 
    "date_of_birth", 
    "email", 
    "first_name", 
    "last_name", 
    "gender", 
    "graduation", 
    "major", 
    "phone_number",
    "school_id",
    "school_name", 
    "shirt_size", 
    "special_needs",
    "dietary_restrictions",
    "updated_at"
]

#
# Define the view forms here using fields from the master list.
#

# The list of keys the user is allowed to get/set, plus metadata for the view.
# Since it's 1:1, we should keep the meta here.
# Edit this to determine what questions should be shown in the form.
hacker_form = collections.OrderedDict([
    ("what_to_learn" , master['what_to_learn']),
    ("background", master['background']),
    ("github", master['github']),
    ("website", master['website']),
    ("mac_address", master['mac_address']),
    ("team_name", master['team_name']),
])

# The MLH View form.  Same template as above, but
# this data is separate from our own.
# Edit this to determine what data from MLH should be shown in the registration form.
mlh_form = collections.OrderedDict([
    ("email", master["email"]),
    ("first_name", master["first_name"]),
    ("last_name", master["last_name"]),
    ("gender", master["gender"]),
    ("graduation", master["graduation"]),
    ("major",master["major"]),
    ("phone_number", master["phone_number"]),
    ("school_name", master["school_name"]),
    ("date_of_birth", master["date_of_birth"]),
    ("shirt_size", master["shirt_size"]),
    ("special_needs", master["special_needs"]),
    ("dietary_restrictions",master["dietary_restrictions"])
])


def validate(user, update_dict, updatable_dict):
    """
    user: the user this data applies to
    update_dict: key-value pairs to set
    updatable_dict: a dict from above with keys:
        editable,
        always, 
        formtype
    """
    status=True
    invalid_key=None
    invalid_value=None
    reason=None

    for key, value in update_dict.items():

        constraints = updatable_dict[key]

        # Make sure the key to be set even exists.

        if key in updatable_dict.keys():

            # Editable check

            if (
                (user.is_editable or constraints['always'])
                and constraints['editable']
                ):
                pass
            else: 
                status = False
                invalid_key = key
                invalid_value = value
                reason="User tried to set an unsettable field"
                break

            # Length Check.

            if constraints['max_length'] >= 0:
                # Max length should be checked.
                if len(value) <= constraints['max_length']:
                    pass
                else:
                    status = False
                    invalid_value = value
                    invalid_key = key
                    reson = "Value exceeds max length"
                    break
            else:
                pass

    return {
        "action": "validate",
        "status": "success" if status else "fail",
        "invalid_key": invalid_key,
        "invalid_value": invalid_value,
        "reason": reason
    }