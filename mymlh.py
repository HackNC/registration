import requests
import urllib
import json

class MlhShim():

    def __init__(self, app_id, secret, redirect_uri):

        self.app_id = app_id
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.grant_type = "authorization_code"


    def get_user(self, auth_code):
        """Given an auth code, run through the Oauth flow and return a user object
        :param: auth_code: See https://my.mlh.io/docs#oauth_flows
        :return: User object
        """
        payload = self._post("https://my.mlh.io/oauth/token", (
            ("client_id", self.app_id),
            ("client_secret", self.secret),
            ("code", auth_code),
            ("redirect_uri", self.redirect_uri),
            ("grant_type", self.grant_type)
        ))
        payload_dict = json.loads(payload)
        access_token = payload_dict['access_token']
        return self._get_user(access_token)

    def get_all(self):
        payload = self._get("https://my.mlh.io/api/v1/users", (
            ("client_id", self.app_id),
            ("secret", self.secret)
        ))
        payload_dict = json.loads(payload)
        return payload_dict

    def _get_user(self, access_token):
        payload = self._get("https://my.mlh.io/api/v1/user", (
            ("access_token", access_token)
        ))
        payload_dict = json.loads(payload)
        return payload_dict

    def _post(self, url, params):
        """
        Make a post request
        :param url: Base url
        :param params: Parameter argument specified as a tuple of 2-tuples
        :return: the response body
        """
        r = requests.post(url + urllib.urlencode(params))
        r.raise_for_status()
        return r.text

    def _get(self, url, params):
        """
        Make Get Request
        :param url: Base URL
        :param params: Parameter argument specified as tuple of 2-tuples
        :return: the response body
        """