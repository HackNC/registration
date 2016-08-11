from flask import request, url_for, render_template, jsonify, redirect, render_template, flash
from flask.ext.login import current_user, login_required

from registration import app, secure_store, settings

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