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
from views import AdminView

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
def load_user(user_email):
    return models.User.query.get(user_email)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('index'))

# 
# Views - Everyone
# 

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
        user_obj = models.HackerUser.update_or_create(user_dict)
        login_user(user_obj)
        return redirect(url_for("dashboard"))
    except RequestException as re:
        print(re)
        return redirect(url_for("logout"))

@app.route("/logout")
def logout():
    logout_user()
    return jsonify(action="logged_out")

@app.route("/")
def index():
    if current_user.is_anonymous:
        return render_template(
            "index.html",
            auth_url=build_auth_url())
    else:
        return redirect(url_for("dashboard"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """
    Successful logins are directed here
    """
    user = current_user

    if request.method == "POST":
        # TODO: Determine if application is in an updatable state (Has application window closed?)
        update_dict = request.form.to_dict()
        update_success = user.update(update_dict)
        if update_success['status'] == "success":
            flash("Update successful")
        else:
            flash("Update failed")

        resume_success = secure_store(request.files, user, "resume")
        if resume_success:
            user.set_resume_location(resume_success['filename'])
            flash("File uploaded")

    return render_template(
        "dashboard.html",
        mlh_data=user.get_friendly_mlh_data(),
        form_data=user.get_friendly_hacknc_data(),
        teammates=user.get_teammates(),
        status_dict=user.get_status(),
        mlh_edit_link=settings.MLH_EDIT_LINK,
    )

@app.route("/api/me", methods=["GET", "POST"])
@login_required
def me():
    """
    a json endpoint for /dashboard data
    TODO: refactor this into /dashboard so that MIME type is considered
    """
    user = current_user
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

# 
# Views - Administrative
# 

@app.route("/admin", methods=["GET"])
@login_required
def admin():
    """
    Administrative users can examine the live registration data
    """
    return AdminView(current_user).get_admin_panel( 
        order=request.args.get("order_by"))

@app.route("/admin/user/<user_email>", methods=["POST", "GET"])
@login_required
def admin_update(user_email):
    """
    This method may be used to set ANY field.  Be careful when using this.
    """
    if current_user.is_admin:
        if request.method == "POST":
            user = load_user(user_email)
            return jsonify(user.admin_update(request.form.to_dict()))
        elif request.method == "GET":
            user = load_user(user_email)
            return AdminView(current_user).api_get(user)   
    else:
        return jsonify(permission="denied"), 403

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
            new_filename = "{fname}_{lname}_{email}_{filetype}{ext}".format(
                fname=user.first_name,
                lname=user.last_name,
                email=user.email,
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
    app.run(debug=debug, port=8080, host="0.0.0.0")
