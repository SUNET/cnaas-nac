import datetime
import os
import random
import time
import unittest

import cnaas_nac.api.external.app
import cnaas_nac.api.internal.app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app_external = cnaas_nac.api.external.app.app
        self.app_internal = cnaas_nac.api.internal.app.app
        self.client_external = self.app_external.test_client()
        self.client_internal = self.app_internal.test_client()
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJpYXQiOjE1NzE" + \
            "wNTk2MTgsIm5iZiI6MTU3MTA1OTYxOCwianRpIjoiNTQ2MDk2YTUtZTNmOS00" + \
            "NzFlLWE2NTctZWFlYTZkNzA4NmVhIiwic3ViIjoiYWRtaW4iLCJmcmVzaCI6Z" + \
            "mFsc2UsInR5cGUiOiJhY2Nlc3MifQ.Sfffg9oZg_Kmoq7Oe8IoTcbuagpP6nu" + \
            "UXOQzqJpgDfqDq_GM_4zGzt7XxByD4G0q8g4gZGHQnV14TpDer2hJXw"
        self.headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }

        if "RADIUS_DEFAULT_VLAN" not in os.environ:
            os.environ["RADIUS_DEFAULT_VLAN"] = str(random.randint(100, 1000))

    def tearDown(self):
        pass

    def test_01_add_user(self):
        json = {
            "username": "unittest",
            "password": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        self.client_internal.post(
            "/api/v1.0/auth", json=json, headers=self.headers)

    def test_02_enable_user(self):
        json = {
            "active": True
        }

        res = self.client_external.put(
            "/api/v1.0/auth/unittest", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["data"][0]["username"], "unittest")
        self.assertEqual(res.json["data"][0]["active"], True)
        self.assertEqual(res.json["data"][0]["vlan"],
                         os.environ["RADIUS_DEFAULT_VLAN"])
        self.assertEqual(res.json["data"][0]["nas_identifier"], "unittest")
        self.assertEqual(res.json["data"][0]["nas_port_id"], "unittest")
        self.assertEqual(res.json["data"][0]["nas_ip_address"], "unittest")
        self.assertEqual(res.json["data"][0]["called_station_id"], "unittest")
        self.assertEqual(res.json["data"][0]["calling_station_id"], "unittest")

    def test_03_authenticate_user(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post("/api/v1.0/auth", json=json)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["Tunnel-Type"]["value"], "VLAN")
        self.assertEqual(res.json["Tunnel-Medium-Type"]["value"], "IEEE-802")
        self.assertEqual(
            res.json["Tunnel-Private-Group-Id"]["value"],
            os.environ["RADIUS_DEFAULT_VLAN"])

        res = self.client_external.get(
            "/api/v1.0/auth/unittest", headers=self.headers)

        self.assertEqual(res.json["data"][0]["reason"], "User accepted")

    def test_04_set_vlan(self):
        json = {
            "vlan": "UNITTEST"
        }

        res = self.client_external.put(
            "/api/v1.0/auth/unittest", json=json, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post("/api/v1.0/auth", json=json)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["Tunnel-Type"]["value"], "VLAN")
        self.assertEqual(res.json["Tunnel-Medium-Type"]["value"], "IEEE-802")
        self.assertEqual(
            res.json["Tunnel-Private-Group-Id"]["value"], "UNITTEST")

    def test_05_set_description(self):
        json = {
            "comment": "UNITTEST"
        }

        res = self.client_external.put(
            "/api/v1.0/auth/unittest", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 200)

        res = self.client_external.get(
            "/api/v1.0/auth/unittest", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["data"][0]["comment"], "UNITTEST")

    def test_06_authenticate_user_new_vlan(self):
        res = self.client_external.get(
            "/api/v1.0/auth/unittest", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["data"][0]["vlan"], "UNITTEST")

    def test_07_wrong_port(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "wrong_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_external.post(
            "/api/v1.0/auth", json=json, headers=self.headers)
        self.assertEqual(res.status_code, 400)

    def test_08_wrong_station(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "wrong_station"
        }

        res = self.client_external.post(
            "/api/v1.0/auth", json=json, headers=self.headers)
        self.assertEqual(res.status_code, 400)

    def test_09_disable_user(self):
        json = {
            "active": False
        }

        res = self.client_external.put(
            "/api/v1.0/auth/unittest", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["data"][0]["username"], "unittest")
        self.assertEqual(res.json["data"][0]["active"], False)
        self.assertEqual(res.json["data"][0]["vlan"], "UNITTEST")
        self.assertEqual(res.json["data"][0]["nas_identifier"], "unittest")
        self.assertEqual(res.json["data"][0]["nas_port_id"], "unittest")
        self.assertEqual(res.json["data"][0]["nas_ip_address"], "unittest")
        self.assertEqual(res.json["data"][0]["called_station_id"], "unittest")
        self.assertEqual(res.json["data"][0]["calling_station_id"], "unittest")

    def test_10_authenticate_user(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post(
            "/api/v1.0/auth", json=json)
        self.assertEqual(res.status_code, 400)

    def test_11_verify_user_data(self):
        res = self.client_external.get(
            "/api/v1.0/auth/unittest", headers=self.headers)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["data"][0]["vlan"], "UNITTEST")
        self.assertEqual(res.json["data"][0]["username"], "unittest")
        self.assertEqual(res.json["data"][0]["nas_identifier"], "unittest")
        self.assertEqual(res.json["data"][0]["nas_port_id"], "unittest")
        self.assertEqual(res.json["data"][0]["nas_ip_address"], "unittest")
        self.assertEqual(res.json["data"][0]["calling_station_id"], "unittest")
        self.assertEqual(res.json["data"][0]["comment"], "UNITTEST")
        self.assertEqual(res.json["data"][0]["reason"], "User is disabled")

    def test_12_move_port(self):
        json = {
            "active": False
        }

        res = self.client_external.put(
            "/api/v1.0/auth/unittest", json=json, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest_new_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest_new_station"
        }

        res = self.client_internal.post("/api/v1.0/auth", json=json)
        self.assertEqual(res.status_code, 400)

        json = {
            "active": True
        }

        res = self.client_external.put(
            "/api/v1.0/auth/unittest", json=json, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest_new_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest_new_station"
        }

        res = self.client_internal.post(
            "/api/v1.0/auth", json=json)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post("/api/v1.0/auth", json=json)
        self.assertEqual(res.status_code, 400)

    def test_13_repeated_auth(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest_new_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest_new_station"
        }

        for i in range(20):
            res = self.client_internal.post("/api/v1.0/auth", json=json)
            self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest_wrong_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest_new_station"
        }

        for i in range(20):
            res = self.client_internal.post("/api/v1.0/auth", json=json)
            self.assertEqual(res.status_code, 400)

        json = {
            "username": "unittest_wrong",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest_new_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest_new_station"
        }

        for i in range(20):
            res = self.client_internal.post("/api/v1.0/auth", json=json)
            self.assertEqual(res.status_code, 400)

    def test_14_disable_port_lock(self):
        os.environ["RADIUS_NO_PORT_LOCK"] = "yes"
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "definetly_wrong_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest_wrong",
            "called_station_id": "unittest_wrong"
        }

        res = self.client_internal.post(
            "/api/v1.0/auth", json=json)
        self.assertEqual(res.status_code, 200)

        os.environ["RADIUS_NO_PORT_LOCK"] = "no"
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "definetly_wrong_port_again",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest_wrong_again",
            "called_station_id": "unittest_wrong_again"
        }

        res = self.client_internal.post(
            "/api/v1.0/auth", json=json)
        self.assertEqual(res.status_code, 400)

    def test_15_add_user_wrong_time(self):
        date = datetime.datetime.now() + datetime.timedelta(minutes=1)
        year = date.year
        month = date.month
        day = date.day
        hour = date.hour
        minute = date.minute

        startstr = f"{year}-{month}-{day} {hour}:{minute}"

        date = datetime.datetime.now() + datetime.timedelta(minutes=-100)
        year = date.year
        month = date.month
        day = date.day
        hour = date.hour
        minute = date.minute

        stopstr = f"{year}-{month}-{day} {hour}:{minute}"

        json = {
            "username": "unittest_wrong_accesstime",
            "password": "unittest_wrong_accesstime",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest",
            "access_start": startstr,
            "access_stop": startstr
        }

        res = self.client_external.post(
            "/api/v1.0/auth", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 400)

        res = self.client_external.delete(
            "/api/v1.0/auth/unittest_wrong_accesstime", headers=self.headers)
        self.assertEqual(res.status_code, 400)

        json = {
            "username": "unittest_wrong_accesstime",
            "password": "unittest_wrong_accesstime",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest",
            "access_start": startstr,
            "access_stop": stopstr
        }

        res = self.client_external.post(
            "/api/v1.0/auth", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 400)

        res = self.client_external.delete(
            "/api/v1.0/auth/unittest_wrong_accesstime", headers=self.headers)
        self.assertEqual(res.status_code, 400)

        json = {
            "username": "unittest_wrong_accesstime",
            "password": "unittest_wrong_accesstime",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest",
            "access_start": "asdasd",
            "access_stop": stopstr
        }

        res = self.client_external.post(
            "/api/v1.0/auth", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 400)

        res = self.client_external.delete(
            "/api/v1.0/auth/unittest_wrong_accesstime", headers=self.headers)
        self.assertEqual(res.status_code, 400)

        json = {
            "username": "unittest_wrong_accesstime",
            "password": "unittest_wrong_accesstime",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest",
            "access_start": startstr,
            "access_stop": "asdasd"
        }

        res = self.client_external.post(
            "/api/v1.0/auth", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 400)

        res = self.client_external.delete(
            "/api/v1.0/auth/unittest_wrong_accesstime", headers=self.headers)
        self.assertEqual(res.status_code, 400)

    def test_16_add_user_access_time(self):
        date = datetime.datetime.now() + datetime.timedelta(minutes=1)
        year = date.year
        month = date.month
        day = date.day
        hour = date.hour
        minute = date.minute

        startstr = f"{year}-{month}-{day} {hour}:{minute}"

        date = datetime.datetime.now() + datetime.timedelta(minutes=2)
        year = date.year
        month = date.month
        day = date.day
        hour = date.hour
        minute = date.minute

        stopstr = f"{year}-{month}-{day} {hour}:{minute}"

        json = {
            "username": "unittest_accesstime",
            "password": "unittest_accesstime",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest",
            "access_start": startstr,
            "access_stop": stopstr
        }

        res = self.client_external.post(
            "/api/v1.0/auth", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 200)

        res = self.client_internal.post("/api/v1.0/auth", json=json)

        self.assertEqual(res.status_code, 400)

        json = {
            "active": True
        }

        res = self.client_external.put(
            "/api/v1.0/auth/unittest_accesstime", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest_accesstime",
            "password": "unittest_accesstime",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post("/api/v1.0/auth", json=json)

        self.assertEqual(res.status_code, 400)

        time.sleep(65)

        res = self.client_internal.post("/api/v1.0/auth", json=json)

        self.assertEqual(res.status_code, 200)

        time.sleep(100)

        res = self.client_internal.post("/api/v1.0/auth", json=json)

        self.assertEqual(res.status_code, 400)

    def test_17_export_csv(self):
        headers = self.headers.copy()
        headers["Content-Type"] = "text/csv"

        json = {
            "username": "unittest_export",
            "password": "unittest_export",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_external.post(
            "/api/v1.0/auth", json=json, headers=self.headers)

        self.assertEqual(res.status_code, 200)

        res = self.client_external.get("/api/v1.0/auth", headers=headers)

        self.assertEqual(res.status_code, 200)

        for key in json:
            key_found = False
            if json[key] in res.text:
                key_found = True
            self.assertIsNotNone(key_found)

    def test_18_import_csv(self):
        csv = """username1,password1,True,100,nas_id1,nas_port1,1.2.3.4,calling1,called1,2022-08-24 15:30,2022-09-01 11:00
username2,password2,True,200,nas_id2,nas_port2,2.2.3.4,calling2,called2,2022-08-24 23:30,2022-09-02 22:00
username3,password3,True,300,nas_id3,nas_port3,3.3.3.4,calling3,called3,2033-08-30 15:30,2033-09-03 23:59"""
        headers = self.headers.copy()
        headers["Content-Type"] = "text/csv"

        res = self.client_external.post(
            "/api/v1.0/auth", headers=headers, data=csv)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json["data"][0]["username"], "username1")
        self.assertEqual(res.json["data"][1]["username"], "username2")
        self.assertEqual(res.json["data"][2]["username"], "username3")

        res = self.client_external.get(
            "/api/v1.0/auth/username1", headers=headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.get(
            "/api/v1.0/auth/username2", headers=headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.get(
            "/api/v1.0/auth/username3", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_99_delete_user(self):
        res = self.client_external.delete(
            "/api/v1.0/auth/unittest", headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.delete(
            "/api/v1.0/auth/unittest_wrong", headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.delete(
            "/api/v1.0/auth/unittest_accesstime", headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.delete(
            "/api/v1.0/auth/unittest_export", headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.delete(
            "/api/v1.0/auth/username1", headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.delete(
            "/api/v1.0/auth/username2", headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.delete(
            "/api/v1.0/auth/username3", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        pass
