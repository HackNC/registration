from flask_sqlalchemy import SQLAlchemy, inspect
from flask import escape
from abc import ABCMeta, abstractmethod
from dateutil.relativedelta import relativedelta
import datetime

from . import settings
from . import forms
from . import utilities

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'user'
    
    # User data
    email = db.Column(db.String(forms.get_length("email")), unique=True)
    first_name = db.Column(db.String(forms.get_length("first_name")))
    last_name = db.Column(db.String(forms.get_length("last_name")))
    phone_number = db.Column(db.String(forms.get_length("phone_number")))
    shirt_size = db.Column(db.String(forms.get_length("shirt_size")))

    # System data
    is_admin = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, primary_key=True)
    user_created_at = db.Column(db.DateTime)
    user_last_updated_at = db.Column(db.DateTime)

    # SQLAlchemy inheritance stuff
    discriminator = db.Column(db.String(50))
    __mapper_args__ = {"polymorphic_on": discriminator}

    # the lists of subscribed callback functions
    create_callbacks = []
    update_callbacks = []

    def __init__(self, email):
        self.email = email
        self.user_created_at = datetime.datetime.utcnow()

    def serialize(self):
        return {c: escape(getattr(self, c)) for c in inspect(self).attrs.keys()}

    def get_id(self):
        """
        Given the primary key for User, return an instance of the subclass implementation
        """
        return self.user_id

    def has_role(self, role_name):
        return self.discriminator == role_name

    def user_created(self):
        for fn in self.create_callbacks:
            fn(self)

    def user_updated(self):
        self.user_last_updated_at = datetime.datetime.utcnow()
        db.session.commit()
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
            if data_dict[key]['formtype'] in forms.ignore_types:
                pass
            else:
                data_dict[key]['value'] = escape(sanitize_None(getattr(self, key)))
                key_editable = data_dict[key]['editable']
                data_dict[key]['editable'] = (self.is_editable or data_dict[key]['always']) and key_editable
        
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
        valid_data = forms.validate(self, update_dict, updatable_dictionary)

        if valid_data['status'] == "success":
            
            for key, value in update_dict.items():
                setattr(self, key, sanitize_Blank(value))
            
            try:
                db.session.commit()
                # Process callbacks if everything went fine.
                # TODO: This should maybe be async.
                self.user_updated()
            
            except Exception as e:
                valid_data['status'] = "fail"
                valid_data['exception'] = e
                valid_data['reason'] = "Database constraint violation."
                db.session.rollback()
                return valid_data
        
        else:
            return valid_data
        
        return valid_data
    
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

    @property
    def is_editable(self):
        raise NotImplementedError("is_editable doesn't exist at this level")

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

    @property
    def is_new(self):
        """
        Returns whether or not the user has ever saved before
        """
        return self.user_last_updated_at == None
    


class HackerUser(User, db.Model):

    # The list of keys the user is allowed to get/set, plus metadata for the view.
    # Since it's 1:1, we should keep the meta here.
    user_get_set_dict = forms.hacker_form

    # The list of keys MLH is allowed to set - don't touch this
    mlh_settable_keys = forms.mlh_settable_keys

    # The list of MLH keys the user can set
    mlh_friendly_dict = forms.mlh_form

    # Things MLH knows - these keys are necessary for the app to function
    mlh_id = db.Column(db.INTEGER, unique=True)
    created_at = db.Column(db.DateTime)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(forms.get_length("gender")))
    graduation = db.Column(db.Date)
    major = db.Column(db.String(forms.get_length("major")))
    school_id = db.Column(db.INTEGER)
    school_name = db.Column(db.String(forms.get_length("school_name")))
    special_needs = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)
    dietary_restrictions = db.Column(db.Text)

    # Our extended data - we can modify this
    what_to_learn = db.Column(db.Text)
    resume_location = db.Column(db.String(512))
    background = db.Column(db.Text)
    team_name = db.Column(db.String(forms.get_length("team_name")))
    github = db.Column(db.String(forms.get_length("github")))
    website = db.Column(db.String(forms.get_length("website")))
    travel_cost = db.Column(db.Float)
    
    accepts_mlh_code = db.Column(db.Boolean)
    accepts_mlh_release = db.Column(db.Boolean)

    preferred_travel_method = db.Column(db.String(forms.get_length("preferred_travel_method")))
    needs_reimbursement = db.Column(db.String(forms.get_length("needs_reimbursement")))

    # System data - the system needs these.
    visible_status = db.Column(db.CHAR)
    pending_status = db.Column(db.CHAR)
    can_edit = db.Column(db.Boolean)
    notes = db.Column(db.Text)
    checked_in = db.Column(db.Boolean)
    rsvp = db.Column(db.Boolean)
    rsvp_by = db.Column(db.DateTime)
    apply_date = db.Column(db.DateTime)
    rsvp_date = db.Column(db.DateTime)

    # SQLAlchemy Inheritance stuff
    __tablename__ = 'hacker_user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "hacker_user",
        "inherit_condition": (user_id == User.user_id)
    }

    def __init__(self, email):
        super(HackerUser, self).__init__(email)
        self.is_admin = False
        self.can_edit = True
        self.visible_status = settings.DEFAULT_REGISTRATION_STATUS
        self.pending_status = 'x'
        self.apply_date = datetime.datetime.utcnow()

    def get_teammates(self):
        if self.team_name not in ['', None]:
            teammates = self.query.filter(HackerUser.team_name.ilike(self.team_name))
            teammates = [teammate.first_name + " " + teammate.last_name for teammate in teammates]
            return teammates
        else:
            return ["You're not currently on a team"]

    def get_team_count(self, team_name):
        if team_name not in ['', None]:
            return self.query.filter(HackerUser.team_name.ilike(team_name)).count()
        else:
            return 0

    def set_resume_location(self, resume_location):
        self.resume_location = resume_location
        db.session.commit() 

    def update(self, update_dict, updatable_dictionary):

        # Validate team size.
        if 'team_name' in update_dict.keys():
            if update_dict['team_name'].lower() != self.team_name:
                team_count = self.get_team_count(update_dict['team_name'])
                if team_count >= 4:
                    return {
                        "status":"fail",
                        "reason":"Teams must be limited to 4 members.",
                        "invalid_key":"team_name",
                        "invalid_value":update_dict['team_name'],
                    }

            # Lower case the team name
            update_dict['team_name'] = update_dict['team_name'].lower()
        
        return super(HackerUser, self).update(update_dict, updatable_dictionary)
    
    @property
    def friendly_status(self):
        return utilities.get_by_code(self.visible_status, forms.StatusCodes)

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
            """
            Try to get by MLH ID, then by email.
            If those fail, create a new user
            """
            email = user_dict["email"]
            mlh_id = user_dict["mlh_id"]
            user = None

            if not user:
                user = HackerUser.query.filter_by(mlh_id=mlh_id).first()
            if not user:
                user = HackerUser.query.filter_by(email=email).first()
            

            if user:
                # If we found the user, done
                pass
            else:
                # Else we must create another.
                user = HackerUser(email)
                db.session.add(user)

                for key, value in user_dict.items():
                    if key in user.mlh_settable_keys:
                        setattr(user, key, value)
                    else:
                        # MLH tried to set a key it shouldn't have - panic
                        raise KeyError("MLH Tried to set a key it shouldn't have.")

                db.session.commit()
                user.user_created()
            
            return user

# 
# Model Helpers
# 

def make_migrations(app):
    with app.app_context():
        db.create_all()

def sanitize_None(value):
    """
    When reading the database to the form, change nulls to ''
    """
    return "" if value in [None, "None", "none", "na", "n/a"] else value

def sanitize_Blank(value):
    """
    When reading the form to the db, change '' to nulls
    """
    return None if value in ['', ' '] else value
