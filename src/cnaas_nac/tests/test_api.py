import os
import unittest
import cnaas_nac.api.external.app
import cnaas_nac.api.internal.app
import random


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app_external = cnaas_nac.api.external.app.app
        self.app_internal = cnaas_nac.api.internal.app.app
        self.client_external = self.app_external.test_client()
        self.client_internal = self.app_internal.test_client()
        self.token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJpYXQiOjE1NzE' + \
            'wNTk2MTgsIm5iZiI6MTU3MTA1OTYxOCwianRpIjoiNTQ2MDk2YTUtZTNmOS00' + \
            'NzFlLWE2NTctZWFlYTZkNzA4NmVhIiwic3ViIjoiYWRtaW4iLCJmcmVzaCI6Z' + \
            'mFsc2UsInR5cGUiOiJhY2Nlc3MifQ.Sfffg9oZg_Kmoq7Oe8IoTcbuagpP6nu' + \
            'UXOQzqJpgDfqDq_GM_4zGzt7XxByD4G0q8g4gZGHQnV14TpDer2hJXw'
        self.headers = {'Authorization': 'Bearer ' + self.token}

        if 'RADIUS_DEFAULT_VLAN' not in os.environ:
            os.environ['RADIUS_DEFAULT_VLAN'] = str(random.randint(100, 1000))

    def tearDown(self):
        pass

    def test_01_add_user(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post(
            '/api/v1.0/auth', json=json, headers=self.headers)

    def test_02_enable_user(self):
        json = {
            "active": True
        }

        res = self.client_external.put(
            '/api/v1.0/auth/unittest', json=json, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        self.assertEqual(res.json['data'][0]['username'], 'unittest')
        self.assertEqual(res.json['data'][0]['active'], True)
        self.assertEqual(res.json['data'][0]['vlan'],
                         os.environ['RADIUS_DEFAULT_VLAN'])
        self.assertEqual(res.json['data'][0]['nas_identifier'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_port_id'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_ip_address'], 'unittest')
        self.assertEqual(res.json['data'][0]['called_station_id'], 'unittest')
        self.assertEqual(res.json['data'][0]['calling_station_id'], 'unittest')

    def test_03_authenticate_user(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['Tunnel-Type']['value'], 'VLAN')
        self.assertEqual(res.json['Tunnel-Medium-Type']['value'], 'IEEE-802')
        self.assertEqual(
            res.json['Tunnel-Private-Group-Id']['value'],
            os.environ['RADIUS_DEFAULT_VLAN'])

        res = self.client_external.get(
            '/api/v1.0/auth/unittest', headers=self.headers)
        self.assertEqual(res.json['data'][0]['reason'], 'User accepted')

    def test_04_set_vlan(self):
        json = {
            "vlan": "UNITTEST"
        }

        res = self.client_external.put(
            '/api/v1.0/auth/unittest', json=json, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['Tunnel-Type']['value'], 'VLAN')
        self.assertEqual(res.json['Tunnel-Medium-Type']['value'], 'IEEE-802')
        self.assertEqual(
            res.json['Tunnel-Private-Group-Id']['value'], 'UNITTEST')

    def test_05_set_description(self):
        json = {
            "comment": "UNITTEST"
        }

        res = self.client_external.put(
            '/api/v1.0/auth/unittest', json=json, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = self.client_external.get(
            '/api/v1.0/auth/unittest', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['comment'], 'UNITTEST')

    def test_06_authenticate_user_new_vlan(self):
        res = self.client_external.get(
            '/api/v1.0/auth/unittest', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['vlan'], 'UNITTEST')

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
            '/api/v1.0/auth', json=json, headers=self.headers)
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
            '/api/v1.0/auth', json=json, headers=self.headers)
        self.assertEqual(res.status_code, 400)

    def test_09_disable_user(self):
        json = {
            "active": False
        }

        res = self.client_external.put(
            '/api/v1.0/auth/unittest', json=json, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        self.assertEqual(res.json['data'][0]['username'], 'unittest')
        self.assertEqual(res.json['data'][0]['active'], False)
        self.assertEqual(res.json['data'][0]['vlan'], 'UNITTEST')
        self.assertEqual(res.json['data'][0]['nas_identifier'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_port_id'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_ip_address'], 'unittest')
        self.assertEqual(res.json['data'][0]['called_station_id'], 'unittest')
        self.assertEqual(res.json['data'][0]['calling_station_id'], 'unittest')

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
            '/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 400)

    def test_11_verify_user_data(self):
        res = self.client_external.get(
            '/api/v1.0/auth/unittest', headers=self.headers)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['vlan'], 'UNITTEST')
        self.assertEqual(res.json['data'][0]['username'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_identifier'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_port_id'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_ip_address'], 'unittest')
        self.assertEqual(res.json['data'][0]['calling_station_id'], 'unittest')
        self.assertEqual(res.json['data'][0]['comment'], 'UNITTEST')
        self.assertEqual(res.json['data'][0]['reason'], 'User is disabled')

    def test_12_move_port(self):
        json = {
            "active": False
        }

        res = self.client_external.put(
            '/api/v1.0/auth/unittest', json=json, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest_new_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest_new_station"
        }

        res = self.client_internal.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 400)

        json = {
            "active": True
        }

        res = self.client_external.put(
            '/api/v1.0/auth/unittest', json=json, headers=self.headers)
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
            '/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client_internal.post('/api/v1.0/auth', json=json)
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
            res = self.client_internal.post('/api/v1.0/auth', json=json)
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
            res = self.client_internal.post('/api/v1.0/auth', json=json)
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
            res = self.client_internal.post('/api/v1.0/auth', json=json)
            self.assertEqual(res.status_code, 400)

    def test_14_disable_port_lock(self):
        os.environ['RADIUS_NO_PORT_LOCK'] = 'yes'
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "definetly_wrong_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest_wrong",
            "called_station_id": "unittest_wrong"
        }

        res = self.client_internal.post(
            '/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 200)

        os.environ['RADIUS_NO_PORT_LOCK'] = 'no'
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "definetly_wrong_port_again",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest_wrong_again",
            "called_station_id": "unittest_wrong_again"
        }

        res = self.client_internal.post(
            '/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 400)

    def test_99_delete_user(self):
        res = self.client_external.delete(
            '/api/v1.0/auth/unittest', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        res = self.client_external.get(
            '/api/v1.0/auth/unittest', headers=self.headers)
        res = self.client_external.delete(
            '/api/v1.0/auth/unittest_wrong', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        res = self.client_external.get(
            '/api/v1.0/auth/unittest_wrong', headers=self.headers)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'], [])
