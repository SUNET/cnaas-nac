import unittest
import cnaas_nac.api.app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = cnaas_nac.api.app.app
        self.client = self.app.test_client()

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

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

    def test_02_enable_user(self):
        json = {
            "enabled": True
        }

        res = self.client.put('/api/v1.0/auth/unittest', json=json)
        self.assertEqual(res.status_code, 200)

    def test_03_authenticate_user(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['Tunnel-Type']['value'], 'VLAN')
        self.assertEqual(res.json['Tunnel-Medium-Type']['value'], 'IEEE-802')
        self.assertEqual(res.json['Tunnel-Private-Group-Id']['value'], '13')

        res = self.client.get('/api/v1.0/auth/unittest')
        self.assertEqual(res.json['data'][0]['reason'], 'User accepted')

    def test_04_set_vlan(self):
        json = {
            "vlan": "UNITTEST"
        }

        res = self.client.put('/api/v1.0/auth/unittest', json=json)
        self.assertEqual(res.status_code, 200)

    def test_05_authenticate_user_new_vlan(self):
        res = self.client.get('/api/v1.0/auth/unittest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['vlan'], 'UNITTEST')

    def test_06_wrong_port(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "wrong_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

    def test_06_wrong_station(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "wrong_station"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

    def test_07_disable_user(self):
        json = {
            "enabled": False
        }

        res = self.client.put('/api/v1.0/auth/unittest', json=json)
        self.assertEqual(res.status_code, 200)

    def test_08_authenticate_user(self):
        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

    def test_09_verify_user_data(self):
        res = self.client.get('/api/v1.0/auth/unittest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['vlan'], 'UNITTEST')
        self.assertEqual(res.json['data'][0]['username'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_identifier'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_port_id'], 'unittest')
        self.assertEqual(res.json['data'][0]['nas_ip_address'], 'unittest')
        self.assertEqual(res.json['data'][0]['calling_station_id'], 'unittest')
        self.assertEqual(res.json['data'][0]['comment'], '')
        self.assertEqual(res.json['data'][0]['reason'], 'User is disabled')

    def test_10_move_port(self):
        json = {
            "enabled": False
        }

        res = self.client.put('/api/v1.0/auth/unittest', json=json)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest_new_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest_new_station"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

        json = {
            "enabled": True
        }

        res = self.client.put('/api/v1.0/auth/unittest', json=json)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest_new_port",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest_new_station"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "unittest",
            "nas_identifier": "unittest",
            "nas_port_id": "unittest",
            "nas_ip_address": "unittest",
            "calling_station_id": "unittest",
            "called_station_id": "unittest"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

    def test_99_delete_user(self):
        res = self.client.delete('/api/v1.0/auth/unittest')
        self.assertEqual(res.status_code, 200)
        res = self.client.get('/api/v1.0/auth/unittest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'], [])
