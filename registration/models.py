from flask_sqlalchemy import SQLAlchemy, inspect
from abc import ABCMeta, abstractmethod
from dateutil.relativedelta import relativedelta

from . import settings
from . import forms
from . import utilities

db = SQLAlchemy()


class User(db.Model):

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

    # the lists of subscribed callback functions
    create_callbacks = []
    update_callbacks = []

    def __init__(self, email):
        self.email = email

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    def get_id(self):
        """
        Given the primary key for User, return an instance of the subclass implementation
        """
        return self.email

    def has_role(self, role_name):
        return self.discriminator == role_name

    def user_created(self):
        for fn in self.create_callbacks:
            fn(self)

    def user_updated(self):
        for fn in self.update_callbacks:
            fn(self)

    def fill_form(self, form):
        """
        :param form: Takes a form from forms.py The most basic could be 
            { "field_id" : {
                "always": True/False
                } 
            }
        :returns: A filled form.  Most basic could be 
            { "field_id" : {
                "value": "_value_",
                "always": True/False,
                "editable": True/False
                } 
            }      
        """
        data_dict = form
        for key in data_dict.keys():
            data_dict[key]['value'] = sanitize_None(getattr(self, key))
            data_dict[key]['editable'] = self.is_editable or self.data_dict[key]['always']
        return data_dict

    def update(self, update_dict, updatable_dictionary):
        """
        :param update_dict: A dict of key/value pairs.
        :param updatable_dictionary: A form from forms.py
        :returns: {
            "action": "update",
            "status": "success/fail",
            "reason": "fail reason if fail"
            }
        """
        for key, value in update_dict.items():       
            if key in updatable_dictionary.keys():
                if self.is_editable or self.updatable_dictionary[key]['always']:
                    setattr(self, key, value)
                else:
                    return {
                        "action": "update",
                        "status": "fail",
                        "reason": "non-editable field state"} 
            else:
                # Tell the user they tried to set a bad key.  It was probably an accident
                return {
                    "action": "update",
                    "status": "fail", 
                    "reason": "user tried to set unsettable field"}
        db.session.commit()
        
        # Process callbacks if everything went fine.
        # TODO: This should maybe be async.
        self.user_updated()
        
        return {
            "action":"update",
            "status":"success"} 
    
    def admin_update(self, update_dict):
        for key, value in update_dict.items():
            print(key, value)
            setattr(self, key, value)
        db.session.commit()
        return {
            "action": "admin_update",
            "status":"success"
        }

    @staticmethod
    def register_create_callback(callback):
        User.create_callbacks.append(callback)

    @staticmethod
    def register_update_callback(callback):
        User.update_callbacks.append(callback)

    # Flask Login Stuff
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False


class HackerUser(User, db.Model):

    # The list of keys the user is allowed to get/set, plus metadata for the view.
    # Since it's 1:1, we should keep the meta here.
    user_get_set_dict = forms.hacker_get_set_dict

    # The list of keys MLH is allowed to set - don't touch this
    mlh_settable_keys = forms.mlh_settable_keys

    # The list of MLH keys the user can set
    mlh_friendly_dict = forms.mlh_friendly_names

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
        self.registration_status = settings.DEFAULT_REGISTRATION_STATUS

    def get_teammates(self):
        if self.team_name is not None and self.team_name is not "":
            teammates = self.query.filter(HackerUser.team_name.ilike(self.team_name))
            teammates = [teammate.first_name + " " + teammate.last_name for teammate in teammates]
            return teammates
        else:
            return ["You're not currently on a team"]

    def set_resume_location(self, resume_location):
        self.resume_location = resume_location
        db.session.commit() 
    
    @property
    def friendly_status(self):
        return utilities.get_by_code(self.registration_status, forms.StatusCodes)

    @property
    def isOver18(self):
        return "Y" \
            if self.date_of_birth <= settings.DATE_OF_HACKATHON - relativedelta(years=18) \
            else "N"

    @property
    def is_editable(self):
        return self.friendly_status['editable_state']

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

            user.user_created()
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
