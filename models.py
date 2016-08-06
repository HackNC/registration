from flask_sqlalchemy import SQLAlchemy, inspect

import settings

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
        "gender", 
        "graduation", 
        "last_name", 
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
        for key, value in update_dict:
            
            if key in self.settable_keys:
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
            teammates = self.query.filter(self.column.ilike(self.team_name))
            teammate_ids = [teammate.id for teammate in teammates]
            return teammate_ids         
        else:
            return []

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