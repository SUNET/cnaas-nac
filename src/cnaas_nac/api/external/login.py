import json

import requests
from authlib.integrations.base_client.errors import (MismatchingStateError,
                                                     OAuthError)
from authlib.integrations.flask_client.apps import FlaskOAuth2App
from cnaas_nac.api.generic import empty_result
from cnaas_nac.api.security import get_identity
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import current_app, make_response, redirect, request, url_for
from flask_restx import Namespace, Resource
from requests.models import PreparedRequest

logger = get_logger()


api = Namespace(
    "oidc",
    description="API for handling auth",
    prefix="/api/{}".format(__api_version__),
)


class LoginApi(Resource):
    def get(self):
        oauth_client = current_app.extensions["authlib.integrations.flask_client"]
        redirect_uri = url_for("oidc_auth_api", _external=True)

        logger.info(f"Redirecting user to login page: {redirect_uri}")

        return oauth_client.connext.authorize_redirect(redirect_uri)


class AuthApi(Resource):
    def get(self):
        """Function to authenticate the user.
        This API call is called by the OAUTH login after the user has logged in.
        We get the users token and redirect them to right page in the frontend.

        Returns:
            A HTTP redirect response to the url in the frontend that handles the repsonse after login.
            The access token is a parameter in the url

        """

        oauth_client = current_app.extensions["authlib.integrations.flask_client"]

        try:
            token = oauth_client.connext.authorize_access_token()
        except MismatchingStateError as e:
            logger.error(
                "Exception during authorization of the access token: {}".format(str(e))
            )
            return (
                empty_result(
                    status="error",
                    data="Exception during authorization of the access token. Please try to login again.",
                ),
                502,
            )
        except OAuthError as e:
            logger.error(
                "Missing information needed for authorization: {}".format(str(e))
            )
            return (
                empty_result(
                    status="error",
                    data="The server is missing some information that is needed for authorization.",
                ),
                500,
            )

        url = "https://google.com"
        parameters = {"token": token["access_token"]}

        if "userinfo" in token and "preferred_username" in token["userinfo"]:
            parameters["username"] = token["userinfo"]["preferred_username"]

        req = PreparedRequest()
        req.prepare_url(url, parameters)
        resp = redirect(req.url, code=302)

        if "refresh_token" in token:
            resp.set_cookie(
                "REFRESH_TOKEN",
                token["refresh_token"],
                httponly=True,
                secure=True,
                samesite="None",
                path="/api/v1.0/oidc/refresh",
                max_age=60 * 60 * 24 * 14,
            )
        return resp


class RefreshApi(Resource):
    def post(self):
        oauth_client = current_app.extensions["authlib.integrations.flask_client"]
        oauth_client_connext: FlaskOAuth2App = oauth_client.connext
        token_string = request.headers.get("Authorization").split(" ")[-1]
        oauth_client_connext.token = token_string
        oauth_client_connext.load_server_metadata()
        url = oauth_client_connext.server_metadata["token_endpoint"]

        ret = requests.post(
            url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": request.cookies.get("REFRESH_TOKEN"),
                "client_id": oauth_client_connext.client_id,
                "client_secret": oauth_client_connext.client_secret,
            },
        )
        refresh_data: dict = ret.json()

        new_refresh_token = refresh_data.pop("refresh_token", None)

        resp = make_response(
            json.dumps(empty_result(status="success", data=refresh_data)), 200
        )
        resp.headers["Content-Type"] = "application/json"

        if new_refresh_token:
            resp.set_cookie(
                "REFRESH_TOKEN",
                new_refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                path="/api/v1.0/auth/refresh",
                max_age=60 * 60 * 24 * 14,
            )
        return resp


class IdentityApi(Resource):
    def get(self):
        identity = get_identity()
        return identity


api.add_resource(LoginApi, "/login")
api.add_resource(AuthApi, "/auth")
api.add_resource(IdentityApi, "/identity")
