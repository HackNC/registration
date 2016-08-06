import sys
from flask import Flask, request, url_for, render_template, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import URL
from requests import RequestException
from flask.ext.login import LoginManager, current_user, login_required, login_user

import mymlh
import models
import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = URL(**settings.DATABASE)
app.secret_key = settings.SECRET_KEY
models.db.init_app(app)
mlh_shim = mymlh.MlhShim(
    settings.MYMLH["app_id"],
    settings.MYMLH["secret"],
    settings.MYMLH["redirect_uri"]
)
login_manager = LoginManager()
login_manager.init_app(app)

# 
# Login handlers
# 

@login_manager.user_loader
def load_user(user_id):
    return models.SessionUser.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')

# 
# The Views
# 

@app.route("/")
def index():
    if current_user.is_anonymous:
        auth_url = build_auth_url()
        return redirect(auth_url)
    else:
        return redirect(url_for("dashboard"))

@login_required
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """
    Successful logins are directed here
    """
    return jsonify(**{"id": current_user.id})

@login_required
@app.route("/admin", methods=["GET"])
def admin():
    """
    Administrative users can examine the live registration data
    """
    if current_user.is_admin:
        return jsonify(**mlh_shim.get_all())
    else:
        return jsonify(permission="denied"), 403

@app.route("/login")
def login():
    """
    Login should only be accessed as a callback from MLH.
    """
    user_dict = {}
    auth_code = ""
    
    # There should be a "code" in the url string
    try:
        auth_code = request.args.get("code")
    except:
        return redirect(url_for("index"))
    
    # The code should be a valid auth token.
    try:
        user_dict = mlh_shim.get_user(auth_code)
        user_obj = models.update_or_create(user_dict)
        login_user(user_obj)
        return redirect(url_for("dashboard"))
    except RequestException as re:
        print(re)
        return redirect(url_for("logout"))

@app.route("/logout")
def logout():
    logout_user()
    return jsonify(action="logged_out")

# 
# Helpers
# 

def build_auth_url():
    return settings.AUTH_URL.format(
        client_id=settings.MYMLH['app_id'],
        callback_uri=settings.CALLBACK_URI
    )

if __name__ == "__main__":
    debug = "debug" in sys.argv
    migrate = "migrate" in sys.argv
    if migrate:
        models.make_migrations(app)
    app.run(debug=debug, port=80, host="0.0.0.0")
