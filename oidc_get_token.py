import os
import sys

from typing import Optional

import requests


def get_token() -> Optional[str]:
    try:
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": os.environ["OIDC_CLIENT_ID"],
            "client_secret": os.environ["OIDC_CLIENT_SECRET"],
        }
        auth_response = requests.post(
            os.environ["OIDC_TOKEN_ENDPOINT"],
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5,
        )
        auth_response.raise_for_status()
        token = auth_response.json()["access_token"]
        return token
    except Exception as e:
        raise ValueError("Could not get JWT token: {}".format(e))
        return None


if __name__ == "__main__":
    args_failure = False

    if "OIDC_TOKEN_ENDPOINT" not in os.environ:
        print("OIDC_TOKEN_ENDPOINT not set")
        args_failure = True
    if "OIDC_CLIENT_ID" not in os.environ:
        print("OIDC_CLIENT_ID not set")
        args_failure = True

    if "OIDC_CLIENT_SECRET" not in os.environ:
        print("OIDC_CLIENT_SECRET not set")
        args_failure = True

    if args_failure:
        sys.exit(1)

    print(get_token())
