from pyrad.client import Client
from pyrad.dictionary import Dictionary

from cnaas_nac.tools.log import get_logger


logger = get_logger()


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
        except Exception:
            raise Exception('Failed to send CoA packet, is NAS reachable?')

        return 'Port bounced'
