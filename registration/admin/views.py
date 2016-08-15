from flask import request, url_for, render_template, jsonify, redirect, render_template, flash
from flask_login import current_user, login_required

from registration import app, load_user

from . import renderers

# 
# Views - Administrative
# 

@app.route("/admin", methods=["GET"])
@login_required
def admin():
    """
    Administrative users can examine the live registration data
    """
    return renderers.AdminView(current_user).get_admin_panel( 
        order=request.args.get("order_by"),
        ufilter=request.args.get("filter"))

@app.route("/admin/user/<user_email>", methods=["POST", "GET"])
@login_required
def admin_update(user_email):
    """
    This method may be used to set ANY field.  Be careful when using this.
    """
    if current_user.is_admin:
        if request.method == "POST":
            user = load_user(user_email)
            success_status = user.admin_update(request.form.to_dict())
            if success_status['status'] == 'success':
                return redirect(url_for('admin'))
            else:
                return jsonify(**success_status)
        elif request.method == "GET":
            user = load_user(user_email)
            return renderers.AdminView(current_user).api_get(user)   
    else:
        return jsonify(permission="denied"), 403
