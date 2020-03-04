import unittest
import cnaas_nac.api.app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = cnaas_nac.api.app.app
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_01_test_eap_user(self):
        json = {
            "username": "eaptest",
            "nas_identifier": "eaptest",
            "nas_port_id": "eaptest",
            "nas_ip_address": "eaptest",
            "calling_station_id": "eaptest",
            "called_station_id": "eaptest",
            "eap": "eap"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/api/v1.0/auth/eaptest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'], [])

    def test_02_add_and_enable_eap_user(self):
        json = {
            "username": "eaptest",
            "nas_identifier": "eaptest",
            "nas_port_id": "eaptest",
            "nas_ip_address": "eaptest",
            "calling_station_id": "eaptest",
            "called_station_id": "eaptest"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

        json = {
            "enabled": True
        }

        res = self.client.put('/api/v1.0/auth/eaptest', json=json)
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/api/v1.0/auth/eaptest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['reason'], 'User disabled.')
        self.assertEqual(res.json['data'][0]['vlan'], '13')

    def test_03_eap_user_change_port(self):
        json = {
            "enabled": True
        }

        res = self.client.put('/api/v1.0/auth/eaptest', json=json)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "eaptest",
            "nas_identifier": "eaptest2",
            "nas_port_id": "eaptest2",
            "nas_ip_address": "eaptest2",
            "calling_station_id": "eaptest2",
            "called_station_id": "eaptest2",
            "eap": "eap2"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/api/v1.0/auth/eaptest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['reason'], '')
        self.assertEqual(res.json['data'][0]['vlan'], '13')

    def test_04_eap_unknown_user(self):
        json = {
            "username": "eaptest_unknown",
            "nas_identifier": "eaptest",
            "nas_port_id": "eaptest",
            "nas_ip_address": "eaptest",
            "calling_station_id": "eaptest",
            "called_station_id": "eaptest",
            "eap": "eap"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/api/v1.0/auth/eaptest_unknown')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'], [])

    def test_05_set_eap_vlan(self):
        json = {
            "vlan": "EAPTEST"
        }

        res = self.client.put('/api/v1.0/auth/eaptest', json=json)
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/api/v1.0/auth/eaptest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['vlan'], 'EAPTEST')

    def test_06_disable_eap_user(self):
        json = {
            "enabled": False
        }

        res = self.client.put('/api/v1.0/auth/eaptest', json=json)
        self.assertEqual(res.status_code, 200)

        json = {
            "username": "eaptest",
            "nas_identifier": "eaptest",
            "nas_port_id": "eaptest",
            "nas_ip_address": "eaptest",
            "calling_station_id": "eaptest",
            "called_station_id": "eaptest",
            "eap": "eap"
        }

        res = self.client.post('/api/v1.0/auth', json=json)
        self.assertEqual(res.status_code, 404)

    def test_07_verify_user_eap_data(self):
        res = self.client.get('/api/v1.0/auth/eaptest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'][0]['username'], 'eaptest')
        self.assertEqual(res.json['data'][0]['vlan'], 'EAPTEST')
        self.assertEqual(res.json['data'][0]['nas_identifier'], 'eaptest')
        self.assertEqual(res.json['data'][0]['nas_port_id'], 'eaptest')
        self.assertEqual(res.json['data'][0]['nas_ip_address'], 'eaptest')
        self.assertEqual(res.json['data'][0]['calling_station_id'], 'eaptest')
        self.assertEqual(res.json['data'][0]['comment'], '')
        self.assertEqual(res.json['data'][0]['reason'], '')

    def test_10_delete_eap_user(self):
        res = self.client.delete('/api/v1.0/auth/eaptest')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/api/v1.0/auth/eaptest')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['data'], [])
