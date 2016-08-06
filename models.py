from flask_sqlalchemy import SQLAlchemy

import settings

db = SQLAlchemy()

class User(db.Model):

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
    shirt_size = db.Column(db.String(32))
    special_needs = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)

    # Our extended data

    what_to_learn = db.Column(db.Text)
    resume_location = db.Column(db.String(256))
    background = db.Column(db.Text)

    # Application fields

    is_admin = db.Column(db.Boolean)

    def __init__(self, id):
        self.id = id
        self.is_admin = False

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
        setattr(user, key, value)
    
    db.session.commit()
    
    return user


def make_migrations(app):
    with app.app_context():
        db.create_all()