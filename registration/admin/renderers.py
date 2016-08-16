from flask import render_template, jsonify

from .. import models, utilities, forms

class AdminView():

    def __init__(self, user):
        """
        Given a user, create their admin view.
        """
        self.user = user
        self.permission_denied = {"status": "permission_denied"}

    def get_admin_panel(self, order=None, ufilter=None):
        if self.user.is_admin:
            users = users = models.HackerUser.query
            if order or ufilter:
                if order == "school":
                    users = users.order_by(models.HackerUser.school_id)
                elif order == "id":
                    users = users.order_by(models.HackerUser.mlh_id)
                elif order == "status":
                    users = users.order_by(models.HackerUser.registration_status)
                elif order == "over18":
                    users = users.order_by(models.HackerUser.date_of_birth)
                elif order == "team":
                    users = users.order_by(models.HackerUser.team_name)

            return render_template(
                "admin.html",
                users=users,
                statuses=forms.StatusCodes.keys()
            )
        else:
            return jsonify(**self.permission_denied), 403

    def api_get(self, target_user):
        if self.user.is_admin:
            return jsonify(**{
                "user_data": target_user.serialize(),
                "team_mates": target_user.get_teammates()
            })
        else:
            return jsonify(**self.permission_denied), 403
