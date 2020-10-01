from pyrad.client import Client
from pyrad.dictionary import Dictionary


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


if __name__ == '__main__':
    attrs = {
        'Tunnel-Private-Group-Id': '13',
        'Arista-PortFlap': '1'
    }

    c = CoA('localhost', b'testing123')
    print(c.send_packet(attrs=attrs))
