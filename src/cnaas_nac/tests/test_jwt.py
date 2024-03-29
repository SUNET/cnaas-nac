import unittest

import cnaas_nac.api.external.app
from cnaas_nac.tools.log import get_logger

logger = get_logger()


class JwtTests(unittest.TestCase):
    def setUp(self):
        self.app_external = cnaas_nac.api.external.app.app
        self.client_external = self.app_external.test_client()
        self.token = "this is an invalid token"
        self.headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }
        self.json = {"invalid": "json"}

    def tearDown(self):
        pass

    def test_endpoints(self):
        endpoints = [
            ["/api/v1.0/auth", "GET"],
            ["/api/v1.0/auth", "POST"],
            ["/api/v1.0/auth/testuser", "GET"],
            ["/api/v1.0/auth/testuser", "DELETE"],
            ["/api/v1.0/auth/testuser", "PUT"],
            ["/api/v1.0/vlans", "GET"],
            ["/api/v1.0/vlans/testvlan", "GET"],
            ["/api/v1.0/groups", "GET"],
            ["/api/v1.0/groups", "DELETE"],
            ["/api/v1.0/groups", "POST"],
            ["/api/v1.0/groups/testgroup", "GET"],
            ["/api/v1.0/groups/testgroup", "DELETE"],
            ["/api/v1.0/groups/testgroup", "PUT"],
            ["/api/v1.0/oui", "GET"],
            ["/api/v1.0/oui/aa:bb:cc", "GET"],
            ["/api/v1.0/state", "GET"],
        ]

        for endpoint, method in endpoints:
            logger.info(f"Testing enpoint {endpoint} and method {method}")

            if method == "GET":
                res = self.client_external.get(
                    endpoint, json=self.json, headers=self.headers)

                self.assertNotEqual(res.status_code, 200)

            if method == "DELETE":
                res = self.client_external.delete(
                    endpoint, json=self.json, headers=self.headers)

                self.assertNotEqual(res.status_code, 200)

            if method == "POST":
                res = self.client_external.post(
                    endpoint, json=self.json, headers=self.headers)

                self.assertNotEqual(res.status_code, 200)

            if method == "PUT":
                res = self.client_external.put(
                    endpoint, json=self.json, headers=self.headers)

                self.assertNotEqual(res.status_code, 200)
