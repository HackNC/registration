from flask_sqlalchemy import SQLAlchemy, inspect

db = SQLAlchemy()

class User(db.Model):

    # The list of keys the user is allowed to set via our api.
    hacknc_settable_keys = [
        "what_to_learn", 
        "background",
        "team_name"]

    # The list of keys MLH is allowed to set.
    mlh_settable_keys = [
        "id", 
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
        "updated_at"]

    # Things MLH knows.
    id = db.Column(db.INTEGER, primary_key=True)
    created_at = db.Column(db.DateTime)
    date_of_birth = db.Column(db.Date)
    email = db.Column(db.String(32))
    first_name = db.Column(db.String(32))
    gender = db.Column(db.String(16))
    graduation = db.Column(db.Date)
    last_name = db.Column(db.String(32))
    major = db.Column(db.String(64))
    phone_number = db.Column(db.String(20))
    school_id = db.Column(db.INTEGER)
    school_name = db.Column(db.String(256))
    shirt_size = db.Column(db.String(32))
    special_needs = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)
    dietary_restrictions = db.Column(db.Text)

    # Our extended data
    what_to_learn = db.Column(db.Text)
    resume_location = db.Column(db.String(256))
    background = db.Column(db.Text)
    team_name = db.Column(db.String(32))

    # System data
    is_admin = db.Column(db.Boolean)

    def __init__(self, id):
        self.id = id
        self.is_admin = False

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    def update(self, update_dict):
        for key, value in update_dict.items():
            
            if key in self.hacknc_settable_keys:
                setattr(self, key, value)
            
            else:
                # Tell the user they tried to set a bad key.  It was probably an accident
                return {
                    "status": "fail", 
                    "reason": "user tried to set unsettable field"
                }
        
        db.session.commit()
        return {"status":"success"} 

    def get_teammates(self):
        if self.team_name is not None:
            teammates = self.query.filter(SessionUser.team_name.ilike(self.team_name))
            teammates = [teammate.first_name + " " + teammate.last_name for teammate in teammates]
            return teammates
        else:
            return []

    def get_mlh_data(self):
        mlh_values = [getattr(self, field) for field in self.mlh_settable_keys]
        return zip(self.mlh_settable_keys, mlh_values)

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
        mlh_friendly_values = [getattr(self, field) for field in friendly_names.keys()]
        return zip(friendly_names.values(), mlh_friendly_values)

    def get_friendly_hacknc_data(self):
        """
        Must resturn both the object_key, Friendly Key, help_text, and value for ever item that should be included in the form
        """
        return {
            "what_to_learn" : { 
                "friendly_name": "What do you want to learn?",
                "help_text": "Whether it be virtual reality, the internet of things, or how to scrape together your first webpage, let us know what you're interested in learning!",
                "value": self.what_to_learn
            },
            "background": {
                "friendly_name": "Your Background",
                "help_text": "Tell us a little more about you!  How'd you get into tech?",
                "value": self.background
            },
            "team_name": {
                "friendly_name": "Team Name",
                "help_text": "Create a team by giving us a team name.  Your teammates can all add the same name and get grouped.  This won't affect your application - it's just for fun!",
                "value": self.team_name
            }
        }

    def set_resume_location(self, resume_location):
        self.resume_location = resume_location
        db.session.commit()
    
    def get_hacknc_data(self):
        hacknc_values = [getattr(self, field) for field in self.hacknc_settable_keys]
        return zip(self.hacknc_settable_keys, hacknc_values)

class SessionUser(User):

    is_authenticated=False
    is_active=True
    is_anonymous=True

    def get_id(self):
        return self.id
    
def update_or_create(user_dict):
    uid = user_dict["id"]
    user = SessionUser.query.get(uid)
    
    if user:
        pass
    else:
        user = SessionUser(uid)
        db.session.add(user)

    for key, value in user_dict.items():
        if key in user.mlh_settable_keys:
            setattr(user, key, value)
        else:
            # MLH tried to set a key it shouldn't have - panic
            raise KeyError("MLH Tried to set a key it shouldn't have.")
    
    db.session.commit()
    
    return user


def make_migrations(app):
    with app.app_context():
        db.create_all()