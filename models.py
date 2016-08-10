from flask_sqlalchemy import SQLAlchemy, inspect

import settings
import utilities
from abc import ABCMeta, abstractmethod

db = SQLAlchemy()


class User(db.Model):

    # Flask login stuff
    is_authenticated=False
    is_active=True
    is_anonymous=True

    __tablename__ = 'user'
    
    # User data
    email = db.Column(db.String(32), primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    phone_number = db.Column(db.String(20))
    shirt_size = db.Column(db.String(32))

    # System data
    is_admin = db.Column(db.Boolean)

    # SQLAlchemy inheritance stuff
    discriminator = db.Column(db.String(50))
    __mapper_args__ = {"polymorphic_on": discriminator}

    def __init__(self, email):
        self.email = email


    def get_id(self):
        """
        Given the primary key for User, return an instance of the subclass implementation
        """
        return self.email


class HackerUser(User, db.Model):

    # The list of keys the user is allowed to get/set, plus metadata for the view.
    # Since it's 1:1, we should keep the meta here.
    user_get_set_dict = utilities.hacker_get_set_dict

    # The list of keys MLH is allowed to set - don't touch this
    mlh_settable_keys = utilities.mlh_settable_keys

    # Things MLH knows - these keys are necessary for the app to function
    # TODO: change application to use email as the primary key
    mlh_id = db.Column(db.INTEGER)
    created_at = db.Column(db.DateTime)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(16))
    graduation = db.Column(db.Date)
    major = db.Column(db.String(64))
    school_id = db.Column(db.INTEGER)
    school_name = db.Column(db.String(256))
    special_needs = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)
    dietary_restrictions = db.Column(db.Text)

    # Our extended data - we can modify this
    what_to_learn = db.Column(db.Text)
    resume_location = db.Column(db.String(256))
    background = db.Column(db.Text)
    team_name = db.Column(db.String(32))
    mac_address = db.Column(db.String(20))
    github = db.Column(db.String(128))
    website = db.Column(db.String(128))

    # System data - the system needs these.
    registration_status = db.Column(db.CHAR)
    can_edit = db.Column(db.Boolean)
    notes = db.Column(db.Text)
    checked_in = db.Column(db.Boolean)

    # SQLAlchemy Inheritance stuff
    __tablename__ = 'hacker_user'
    email = db.Column(db.String(32), db.ForeignKey('user.email'), 
        primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "hacker_user",
        "inherit_condition": (email == User.email)}

    def __init__(self, email):
        super(HackerUser, self).__init__(email)
        self.is_admin = False
        self.can_edit = True
        self.registration_status = settings.DEFAULT_USER_STATUS

    def get_id(self):
        return self.email

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    def update(self, update_dict):
        for key, value in update_dict.items():
            
            if key in self.user_get_set_dict.keys():
                if self.is_editable or self.user_get_set_dict[key]['always']:
                    setattr(self, key, value)
                else:
                    return {
                        "action": "update",
                        "status": "fail",
                        "reason": "non-editable field state"
                    }
            
            else:
                # Tell the user they tried to set a bad key.  It was probably an accident
                return {
                    "action": "update",
                    "status": "fail", 
                    "reason": "user tried to set unsettable field"
                }
        
        db.session.commit()
        return {"status":"success"} 

    def get_teammates(self):
        if self.team_name is not None and self.team_name is not "":
            teammates = self.query.filter(HackerUser.team_name.ilike(self.team_name))
            teammates = [teammate.first_name + " " + teammate.last_name for teammate in teammates]
            return teammates
        else:
            return ["You're not currently on a team"]

    def get_friendly_mlh_data(self):
        """
        Returns a dictionary of "Friendly Key" : "Value" pairs
        """
        friendly_names = {
            "date_of_birth": "Date of Birth",
            "email": "Email",
            "first_name": "First Name",
            "last_name": "Last Name",
            "gender": "Gender",
            "graduation": "Graduation",
            "major": "Major",
            "phone_number": "Phone Number",
            "school_name": "School",
            "shirt_size": "Shirt Size", 
            "special_needs": "Special Needs",
            "dietary_restrictions": "Dietary Restrictions"
        }
        mlh_friendly_values = [sanitize_None(getattr(self, field)) for field in friendly_names.keys()]
        return zip(friendly_names.values(), mlh_friendly_values)

    def get_friendly_hacknc_data(self):
        """
        Must resturn both the object_key, Friendly Key, help_text, and value for ever item that should be included in the form
        """
        data_dict = self.user_get_set_dict
        for key in data_dict.keys():
            data_dict[key]['value'] = sanitize_None(getattr(self, key))
            data_dict[key]['editable'] = self.is_editable or self.user_get_set_dict[key]['always']
        return data_dict

    def get_status(self):
        return utilities.get_by_code(self.registration_status)

    def set_resume_location(self, resume_location):
        self.resume_location = resume_location
        db.session.commit()

    def admin_update(self, update_dict):
        for key, value in update_dict.items():
            print(key, value)
            setattr(self, key, value)
        db.session.commit()
        return {
            "action": "admin_update",
            "status":"success"
        } 

    @property
    def is_editable(self):
        return self.get_status()['editable_state']

    @staticmethod
    def update_or_create(user_dict):
        email = user_dict["email"]
        user = HackerUser.query.get(email)
        
        if user:
            pass
        else:
            user = HackerUser(email)
            db.session.add(user)

        for key, value in user_dict.items():
            if key in user.mlh_settable_keys:
                setattr(user, key, value)
            else:
                # MLH tried to set a key it shouldn't have - panic
                raise KeyError("MLH Tried to set a key it shouldn't have.")
        
        db.session.commit()
        
        return user
    
# 
# Model Helpers
# 

def make_migrations(app):
    with app.app_context():
        db.create_all()

def sanitize_None(value):
    return "" if value in [None, "None"] else value
