import enum
import ipaddress
import datetime

from sqlalchemy import Column, Integer, Unicode, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from cnaas_nac.db.session import sqla_session


Base = declarative_base()


class DeviceOui(Base):
    __tablename__ = 'device_oui'
    __table_args__ = (
        None,
        UniqueConstraint('id'),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)
    oui = Column(Unicode(64), nullable=False)
    vlan = Column(Unicode(64), nullable=False)
    description = Column(Unicode(64), nullable=False)

    def as_dict(self):
        """Return JSON serializable dict."""
        d = {}
        for col in self.__table__.columns:
            value = getattr(self, col.name)
            if issubclass(value.__class__, enum.Enum):
                value = value.value
            elif issubclass(value.__class__, Base):
                continue
            elif issubclass(value.__class__, ipaddress.IPv4Address):
                value = str(value)
            elif issubclass(value.__class__, datetime.datetime):
                value = str(value)
            d[col.name] = value
        return d

    @classmethod
    def exists(cls, oui):
        exists = False
        oui = cls.normalize(oui)
        with sqla_session() as session:
            oui: DeviceOui = session.query(DeviceOui).filter(DeviceOui.oui ==
                                                             oui).one_or_none()
            if oui:
                exists = True
        return exists

    @classmethod
    def get_vlan(cls, username):
        oui = cls.normalize(username)
        with sqla_session() as session:
            oui: DeviceOui = session.query(DeviceOui).filter(DeviceOui.oui ==
                                                             oui).one_or_none()
            if oui:
                return oui.vlan
        return None

    @classmethod
    def normalize(cls, oui):
        oui = oui.replace(':', '')
        oui = ':'.join(oui[i:i+2] for i in range(0, 6, 2))
        oui = oui.lower()
        return oui


if __name__ == '__main__':
    print(DeviceOui.normalize('aa:bb:CC'))
    print(DeviceOui.normalize('aabbCC'))
    print(DeviceOui.normalize('aa:bb:CC:DD:EE:ff'))
