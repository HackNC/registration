from flask import request, url_for, render_template, jsonify, redirect, render_template, flash
from flask_login import current_user, login_required

from .. import app, secure_store, settings, forms, utilities

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return jsonify(**{"action":"unknown"})

@app.route("/apply", methods=["GET", "POST"])
@login_required
def apply():
    """
    Successful logins are directed here
    """
    user = current_user

    if request.method == "POST":
        # TODO: Determine if application is in an updatable state (Has application window closed?)
        update_dict = request.form.to_dict()
        # TODO: Validate the form.
        updatable_dictionary = utilities.merge_two_dicts(
            forms.hacker_get_set_dict, forms.mlh_friendly_names)
        
        update_success = user.update(update_dict, updatable_dictionary)
        
        if update_success['status'] == "success":
            flash("Update successful")
        else:
            flash("Update failed")

        resume_success = secure_store(request.files, user, "resume")
        if resume_success:
            user.set_resume_location(resume_success['filename'])
            flash("File uploaded")

    return render_template(
        "apply.html",
        mlh_data=user.fill_form(forms.mlh_friendly_names),
        form_data=user.fill_form(forms.hacker_get_set_dict),
        teammates=user.get_teammates(),
        allowed_extensions=settings.ALLOWED_EXTENSIONS
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
        
        updatable_dictionary = utilities.merge_two_dicts(
            forms.hacker_get_set_dict, forms.mlh_friendly_names)
        
        update_success = user.update(request.form.to_dict(), updatable_dictionary)
        return jsonify(**{
            "action": update_success,
            "user_data":user.serialize(),
            "team_mates": user.get_teammates()
        })

def validate_update(update_form_dict):
    """
    :returns: True/False
    """