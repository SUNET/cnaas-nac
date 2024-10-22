import os

from authlib.integrations.flask_oauth2 import ResourceProtector, current_token
from authlib.oauth2.rfc6749.requests import OAuth2Request
from authlib.oauth2.rfc6750 import BearerTokenValidator
from cnaas_nac.tools.log import get_logger
from cnaas_nac.tools.oidc.key_management import get_key
from cnaas_nac.tools.oidc.oidc_client_call import get_oauth_token_info
from cnaas_nac.tools.oidc.token import Token
from flask_jwt_extended import get_jwt_identity as get_jwt_identity_orig
from flask_jwt_extended import jwt_required
from jose import exceptions, jwt
from jwt.exceptions import (ExpiredSignatureError, InvalidKeyError,
                            InvalidTokenError)

logger = get_logger()


class MyBearerTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string: str) -> Token:
        """Check if token is active.

        If JWT is disabled, we return because no token is needed.

        We decode the header and check if it's good. If not,
        we check if we can validate the user using the userinfo endpoint.

        We decode the token using the keys.
        We first check if we can decode it, if not we request the keys.
        The decode function also checks if it's not expired.
        We get de decoded _token back, but for now we do nothing with this.

        Input
            token_string(str): The tokenstring
        Returns:
            token(dict): Dictionary with access_token, decoded_token, token_type, audience, expires_at

        """

        # If OIDC is disabled, no token is needed (for future use)
        if not os.getenv("OIDC_ENABLED"):
            return "no-token-needed"

        # First decode the header
        try:
            unverified_header = jwt.get_unverified_header(token_string)
        except exceptions.JWSError as e:
            raise InvalidTokenError(e)
        except exceptions.JWTError:
            # check if we can still authenticate the user with user info
            token = Token(token_string, None)
            get_oauth_token_info(token)
            return token

        # get the key
        key = get_key(unverified_header.get("kid"))

        # decode the token
        algorithm = unverified_header.get("alg")
        try:
            decoded_token = jwt.decode(
                token_string,
                key,
                algorithms=algorithm,
                audience="https://norpan.cnaas.sunet.se",
                options={"verify_aud": False},
            )
            # make an token object to make it easier to validate
            token = Token(token_string, decoded_token)
            return token
        except exceptions.ExpiredSignatureError as e:
            raise ExpiredSignatureError(e)
        except exceptions.JWKError as e:
            logger.error("Invalid Key")
            raise InvalidKeyError(e)
        except exceptions.JWTError as e:
            logger.error("Invalid Token")
            raise InvalidTokenError(e)

    def validate_token(self, token, scopes, request: OAuth2Request) -> Token:
        """Check if token matches the requested scopes and user has permission to execute the API call."""

        return token


def get_oauth_identity() -> str:
    """Give back the username of the OAUTH account

    If JWT is disabled, we return "admin".

    We do an api call to request userinfo. This gives back all the userinfo.
    We get the right info from there and return this to the user.

    Returns:
        username(str): Username of the logged in user

    """

    # For now unnecersary, useful when we only use one log in method
    if not os.getenv("OIDC_ENABLED"):
        return "Admin"

    oidc_username_attribute = os.getenv("OIDC_USERNAME_ATTRIBUTE")

    token_info = get_oauth_token_info(current_token)
    if oidc_username_attribute:
        return token_info[oidc_username_attribute]
    elif "client_id" in token_info:
        return token_info["client_id"]
    else:
        error_message = "{} or client_id is a required claim for oauth".format(
            oidc_username_attribute
        )
        logger.error(error_message)
        raise KeyError(error_message)


def get_jwt_identity():
    """This function overides the identity when needed."""
    return get_jwt_identity_orig() if os.getenv("JWT_ENABLED") else "admin"


# check which method we use to log in and load vars needed for that
if os.getenv("OIDC_ENABLED"):
    logger.info("OIDC is enabled")

    oauth_required = ResourceProtector()
    oauth_required.register_token_validator(MyBearerTokenValidator())
    login_required = oauth_required(optional=not os.getenv("OIDC_ENABLED"))
    get_identity = get_oauth_identity
else:
    logger.info("JWT is enabled")

    oauth_required = None
    get_identity = get_jwt_identity
    login_required = jwt_required
