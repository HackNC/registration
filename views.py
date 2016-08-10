from flask import render_template, jsonify
import models

class AdminView():

    def __init__(self, user):
        """
        Given a user, create their admin view.
        """
        self.user = user
        self.permission_denied = {"status": "permission_denied"}

    def get_admin_panel(self, order=None):
        if self.user.is_admin:
            users = None
            if order:
                if order == "school":
                    users = models.SessionUser.query.order_by(models.SessionUser.school_id)
                elif order == "id":
                    users = models.SessionUser.query.order_by(models.SessionUser.mlh_id)
                elif order == "status":
                    users = models.SessionUser.query.order_by(models.SessionUser.registration_status)
            else:
                users = models.HackerUser.query
            return render_template(
                "admin.html",
                users=users
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

class HackerView():

    def __init__(self, user):
        """
        Given a user, create their hacker view
        """
        self.user = user

    def get_dashboard(self):
        pass