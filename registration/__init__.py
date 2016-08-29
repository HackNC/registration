# Standard
import os
from functools import wraps
import ntpath
import logging
from logging import StreamHandler
import sys
# pre-installed
from requests import RequestException
from flask import Flask, request, url_for, jsonify, redirect, render_template
from sqlalchemy.engine.url import URL
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_cors import CORS
# modules
from . import mymlh
from . import models
from . import settings
from . import utilities

# Load app
app = Flask(__name__)

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = URL(**settings.DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
app.config['DEBUG'] = settings.DEBUG
app.secret_key = settings.SECRET_KEY

# Verbose logging in PROD
if app.debug is False:
    handler = StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

# Load sub-modules
CORS(app)
models.db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Load MLH shim
mlh_shim = mymlh.MlhShim(
    settings.MYMLH["app_id"],
    settings.MYMLH["secret"],
    settings.MYMLH["redirect_uri"]
)

#
# Index
#

@app.route("/")
def index():
    if current_user.is_anonymous:
        return render_template(
            "index.html",
            auth_url=utilities.build_auth_url())
    elif current_user.discriminator == "hacker_user":
        return redirect(url_for(settings.DEFAULT_VIEW))
    else:
        return jsonify(action="unknown")

# 
# Login handlers
#

def login_required_or_next(nxt=settings.DEFAULT_VIEW, requires_admin=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            """
            Require the user to be authenticated.
            If not, kick user to MLH and set a cookie for the target page.
            """
            if not current_user.is_authenticated:
                # If not authenticated, set a cookie and redirect.
                target = redirect(utilities.build_auth_url())
                response = app.make_response(target)
                response.set_cookie('next', value=nxt)
                return response

            # If admin required
            if requires_admin and not current_user.is_admin:
                return jsonify(**{"status": "permission_denied"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/login")
def login():
    """
    Login should only be accessed as a callback from MLH.
    """
    user_dict = {}
    auth_code = ""
    nxt = None

    if 'next' in request.cookies:
        if request.cookies['next'] in settings.ALLOWED_PAGES:
            nxt = request.cookies['next']
    
    # There should be a "code" in the url string
    try:
        auth_code = request.args.get("code")
    except:
        return redirect(url_for("index"))
    
    # The code should be a valid auth token.
    try:
        user_dict = mlh_shim.get_user(auth_code)
        user_obj = models.HackerUser.update_or_create(user_dict)
        login_user(user_obj)
        if nxt:
            try:
                target = redirect(url_for(nxt))
                response = app.make_response(target)
                response.set_cookie('next', value='', expires=0)
                return response
            except Exception as e:
                return jsonify(**{
                    "action": "Redirect",
                    "status": "failed",
                    "message": "please log in and retry your request.  Report bugs to bugs@hacknc.com",
                })
        else:
            return redirect(url_for(settings.DEFAULT_VIEW))
    except RequestException as re:
        print(re)
        return redirect(url_for("logout"))

# 
# Helpers
# 

def allowed_file(filename):
    return '.' in filename \
        and filename.rsplit('.', 1)[1] in settings.ALLOWED_EXTENSIONS

def secure_store(requests_files, user, form_file_name):
    # check if the post request has the file part
    if form_file_name not in requests_files:
        # User gave no file.  That's fine.
        return False
    
    else:
        file = request.files[form_file_name]
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # User gave no file.  That's fine.
            return False
        
        if file and allowed_file(file.filename):
            old_name, extension = os.path.splitext(file.filename)
            new_filename = "{fname}_{lname}_{email}_{filetype}{ext}".format(
                fname=user.first_name,
                lname=user.last_name,
                email=user.email,
                filetype=form_file_name,
                ext=extension)
            new_filename = ntpath.split(new_filename)[-1]
            full_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            print("Resume uploaded - " + full_file_path)
            file.save(full_file_path)
            return {
                "action": "uploaded",
                "filename": full_file_path
            }

# Load views - this is how we make sub modules
from .admin import views
from .hacker import views