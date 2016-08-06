import sys
from flask import Flask, request, url_for, render_template, jsonify, redirect
import requests

import mymlh
import settings

app = Flask(__name__)
mlh_shim = mymlh.MlhShim(
    settings.MYMLH["app_id"],
    settings.MYMLH["secret"],
    settings.MYMLH["redirect_uri"]
)

@app.route("/login")
def login():
    auth_code = request.args.get("code")
    user_dict = {}
    try:
        user_dict = mlh_shim.get_user(auth_code)
    except requests.RequestException as re:
        print(re)
        return redirect(url_for("logout"))

    return jsonify(**user_dict)

@app.route("/logout")
def logout():
    return jsonify(status="logged_out")

if __name__ == "__main__":
    debug = sys.argv[1] == "debug"
    app.run(debug=debug, port=5000)