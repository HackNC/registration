from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import URL

import settings

db = SQLAlchemy()

def db_connect(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = URL(**settings.DATABASE)
    global db
    db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.CHAR, primary_key=True)