from pyrad.client import Client
from pyrad.dictionary import Dictionary

from flask import request
from flask_restplus import Resource, Namespace, fields

from cnaas_nac.api.generic import empty_result
from cnaas_nac.tools.log import get_logger

from cnaas_nac.version import __api_version__


logger = get_logger()


api = Namespace('coa', description='Port bounce API',
                prefix='/api/{}'.format(__api_version__))

port_bounce = api.model('bounce', {
    'portname': fields.String(required=True),
    'host': fields.String(required=True),
    'secret': fields.String(required=True)
})


class CoA:
    def __init__(self, host, secret):
        self.client = Client(host, coaport=3799, secret=secret,
                             dict=Dictionary("dictionary"))
        self.client.timeout = 30

    def send_packet(self, attrs=None):
        try:
            self.coa_attrs = {k.replace("-", "_"): attrs[k] for k in attrs}
            self.coa_pkt = self.client.CreateCoAPacket(**self.coa_attrs)
            result = self.client.SendPacket(self.coa_pkt)
        except KeyError as e:
            return 'Failed to send CoA packet, invalid attribute: %s' % (str(e))
        else:
            return 'Failed to send CoA packet: %s (%s)' % (type(e), str(e))

        return result


class BounceApi(Resource):
    @api.expect(port_bounce)
    def post(self):
        """
        Send a CoA-Request to the NAS and tell it to flap the selected
        port.

        The VSA used to flap ports on Airsta switches is
        Arista-PortFlap and must be present in the dictionary.
        """

        json_data = request.get_json()

        logger.info(json_data)

        result = {
            'portname': json_data['portname'],
            'host': json_data['host'],
            'secret': '**********'
        }

        return empty_result(status='success', data=result)


api.add_resource(BounceApi)


if __name__ == '__main__':
    attrs = {
        'Tunnel-Private-Group-Id': '13',
        'Arista-PortFlap': '1'
    }

    c = CoA('localhost', b'testing123')
    print(c.send_packet(attrs=attrs))
