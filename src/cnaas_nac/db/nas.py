import enum
import ipaddress
import datetime

from sqlalchemy import Column, Integer, Unicode, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from cnaas_nac.db.session import sqla_session


Base = declarative_base()


class NasPort(Base):
    __tablename__ = 'nas_port'
    __table_args__ = (
        None,
        UniqueConstraint('id'),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(64), nullable=False)
    nas_identifier = Column(Unicode(64), nullable=False)
    nas_port_id = Column(Unicode(64), nullable=False)
    nas_ip_address = Column(Unicode(64), nullable=False)
    calling_station_id = Column(Unicode(64), nullable=False)
    called_station_id = Column(Unicode(64), nullable=False)

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
    def get(cls, username=None):
        res = []
        with sqla_session() as session:
            if username:
                nas: NasPort = session.query(NasPort).filter(NasPort.username ==
                                                             username).all()
            else:
                nas: NasPort = session.query(NasPort).all()
            if nas is None:
                return None
            for port in nas:
                res.append(port.as_dict())
            return res

    @classmethod
    def add(cls, username, nas_ip_address, nas_identifier, nas_port_id,
            calling_station_id,
            called_station_id):
        if cls.get(username):
            return ''
        with sqla_session() as session:
            nas = NasPort()
            nas.username = username
            nas.nas_ip_address = nas_ip_address
            nas.nas_identifier = nas_identifier
            nas.nas_port_id = nas_port_id
            nas.calling_station_id = calling_station_id
            nas.called_station_id = called_station_id
            session.add(nas)
        return ''

    @classmethod
    def delete(cls, username):
        if not cls.get(username):
            return ''
        with sqla_session() as session:
            nas_ports: NasPort = session.query(NasPort).filter(NasPort.username ==
                                                               username).all()
            for port in nas_ports:
                session.delete(port)
                session.commit()
        return ''
