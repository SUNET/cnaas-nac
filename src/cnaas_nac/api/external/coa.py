from pyrad.client import Client
from pyrad.dictionary import Dictionary

from flask import request
from flask_restplus import Resource, Namespace, fields
from flask_jwt_extended import jwt_required

from cnaas_nac.api.generic import empty_result
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from cnaas_nac.db.user import get_users


logger = get_logger()


api = Namespace('coa', description='Port bounce API',
                prefix='/api/{}'.format(__api_version__))

port_bounce = api.model('bounce', {
    'username': fields.String(required=True),
    'secret': fields.String(required=True)
})


class CoA:
    def __init__(self, host, secret):
        self.client = Client(host, coaport=3799, secret=secret,
                             dict=Dictionary("dictionary"))
        self.client.timeout = 10

    def send_packet(self, attrs=None):
        try:
            self.coa_attrs = {k.replace("-", "_"): attrs[k] for k in attrs}
            self.coa_pkt = self.client.CreateCoAPacket(**self.coa_attrs)
            self.client.SendPacket(self.coa_pkt)
        except Exception as e:
            raise Exception('Failed to send CoA packet, is NAS reachable?')

        return 'Port bounced'


class BounceApi(Resource):
    @api.expect(port_bounce)
    @jwt_required
    def post(self):
        """
        Send a CoA-Request to the NAS and tell it to flap the selected
        port.

        The VSA used to flap ports on Airsta switches is
        Arista-PortFlap and must be present in the dictionary.
        """

        json_data = request.get_json()

        if json_data is None:
            return empty_result(status='error', data='Missing JSON data')
        if 'username' not in json_data:
            return empty_result(status='error', data='Username')
        if 'secret' not in json_data:
            return empty_result(status='error', data='Secret required')

        userdata = get_users(field='username', condition=json_data['username'])

        if userdata is []:
            return empty_result(status='error', data='User not found')

        nas_ip_address = userdata[0]['nas_ip_address']
        nas_port_id = userdata[0]['nas_port_id']

        attrs = {
            'NAS-IP-Address': nas_ip_address,
            'NAS-Port-Id': nas_port_id,
            'Arista-PortFlap': '1'
        }

        secret = str.encode(json_data['secret'])

        try:
            coa_request = CoA(nas_ip_address, secret)
            res = coa_request.send_packet(attrs=attrs)
        except Exception as e:
            return empty_result(status='error', data=str(e))

        return empty_result(status='success', data=res)


if __name__ == '__main__':
    attrs = {
        'Tunnel-Private-Group-Id': '13',
        'Arista-PortFlap': '1'
    }

    c = CoA('localhost', b'testing123')
    print(c.send_packet(attrs=attrs))
else:
    api.add_resource(BounceApi, '')
