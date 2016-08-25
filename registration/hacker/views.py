from flask import request, url_for, render_template, jsonify, redirect, render_template, flash
from flask_login import current_user, login_required

from .. import app, secure_store, settings, forms, utilities, login_required_or_next

@app.route("/dashboard", methods=["GET"])
@login_required_or_next(nxt="dashboard")
def dashboard():
    return render_template(
        "dashboard.html",
        status=utilities.get_by_code(current_user.visible_status, forms.StatusCodes),
        teammates=current_user.get_teammates()
    )

@app.route("/apply", methods=["GET", "POST"])
@login_required_or_next(nxt="apply")
def apply():
    """
    Successful logins are directed here
    """
    user = current_user

    if request.method == "POST":
        # TODO: Determine if application is in an updatable state (Has application window closed?)
        update_dict = request.form.to_dict()

        updatable_dictionary = utilities.merge_two_dicts(
            forms.hacker_form, forms.mlh_form)
        
        update_success = user.update(update_dict, updatable_dictionary)
        
        if update_success['status'] == "success":
            flash("Application submitted.  You may submit as often as you wish while applications are open.")
        else:
            flash("Update failed on {invalid_key} = {invalid_value}! reason: {reason} {bug_report}".format(
                reason=update_success['reason'],
                invalid_value=update_success['invalid_value'],
                invalid_key=update_success['invalid_key'],
                bug_report="Report bugs to bugs@hacknc.com"))
            print(update_success)

        resume_success = secure_store(request.files, user, "resume")
        if resume_success:
            user.set_resume_location(resume_success['filename'])
            flash("File uploaded")

    return render_template(
        "apply.html",
        mlh_data=user.fill_form(forms.mlh_form),
        form_data=user.fill_form(forms.hacker_form),
        teammates=user.get_teammates(),
        allowed_extensions=settings.ALLOWED_EXTENSIONS
    )

@app.route("/api/me", methods=["GET", "POST"])
@login_required_or_next(nxt="me")
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
            forms.hacker_form, forms.mlh_form)
        
        update_success = user.update(request.form.to_dict(), updatable_dictionary)
        return jsonify(**{
            "action": update_success,
            "user_data":user.serialize(),
            "team_mates": user.get_teammates()
        })