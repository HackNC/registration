import sys
import os

from requests import RequestException
from flask import Flask, request, url_for, render_template, jsonify, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import URL
from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user
from flask_cors import CORS, cross_origin

import mymlh
import models
import settings

# Load app
app = Flask(__name__)

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = URL(**settings.DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
app.secret_key = settings.SECRET_KEY

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
    user = models.SessionUser.query.get(current_user.id)

    if request.method == "POST":
        # TODO: Determine if application is in an updatable state (Has application window closed?)
        update_success = user.update(request.form.to_dict())
        if update_success['status'] == "success":
            flash("Update successful")
        else:
            flash("Update failed")

        if secure_store(request.files, user, "resume"):
            flash("File uploaded")

    return render_template(
        "dashboard.html",
        mlh_data=user.get_mlh_data(),
        hacknc_data=user.get_hacknc_data(),
        teammates=user.get_teammates(),
        mlh_edit_link=settings.MLH_EDIT_LINK,
        user=user)


@login_required
@app.route("/api/me", methods=["GET", "POST"])
def me():
    """
    An API endpoint for /dashboard data
    """
    user = models.SessionUser.query.get(current_user.id)
    if request.method == "GET":
        return jsonify(**{
            "user_data": user.serialize(),
            "team_mates": user.get_teammates()
        })
    elif request.method == "POST":
        update_success = user.update(request.form)
        return jsonify(**{
            "action": update_success,
            "user_data":user.serialize()
        })

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
            new_filename = "{fname}_{lname}_{id}_{filetype}{ext}".format(
                fname=user.first_name,
                lname=user.last_name,
                id=user.id,
                filetype=form_file_name,
                ext=extension)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            return {
                "action": "uploaded",
                "filename": new_filename
            }

if __name__ == "__main__":
    debug = "debug" in sys.argv
    migrate = "migrate" in sys.argv
    if migrate:
        models.make_migrations(app)
    app.run(debug=debug, port=80, host="0.0.0.0")
