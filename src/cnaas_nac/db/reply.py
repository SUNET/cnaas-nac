import enum
import ipaddress
import datetime

from cnaas_nac.db.session import sqla_session
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Reply(Base):
    __tablename__ = 'radreply'
    __table_args__ = (
        None,
        UniqueConstraint('id'),
    )
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(64), nullable=False)
    attribute = Column(Unicode(64), nullable=False)
    op = Column(Unicode(2), nullable=False)
    value = Column(Unicode(253), nullable=False)

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
        result = []
        with sqla_session() as session:
            if username:
                replymsg: Reply = session.query(Reply).filter(Reply.username ==
                                                              username).order_by(Reply.id).all()
            else:
                replymsg: Reply = session.query(Reply).order_by(Reply.id).all()
            if replymsg is None:
                return result
            for _ in replymsg:
                result.append(_.as_dict())
        return result

    @classmethod
    def add(cls, username, vlan):
        if cls.get(username) != []:
            return 'Reply already exists'
        with sqla_session() as session:
            tunnel_type = Reply()
            tunnel_type.username = username
            tunnel_type.attribute = 'Tunnel-Type'
            tunnel_type.op = '='
            tunnel_type.value = 'VLAN'
            session.add(tunnel_type)
            medium_type = Reply()
            medium_type.username = username
            medium_type.attribute = 'Tunnel-Medium-Type'
            medium_type.op = '='
            medium_type.value = 'IEEE-802'
            session.add(medium_type)
            tunnel_id = Reply()
            tunnel_id.username = username
            tunnel_id.attribute = 'Tunnel-Private-Group-Id'
            tunnel_id.op = '='
            tunnel_id.value = vlan
            session.add(tunnel_id)
        return ''

    @classmethod
    def delete(cls, username):
        with sqla_session() as session:
            instance = session.query(Reply).filter(Reply.username ==
                                                   username).all()
            if not instance:
                return 'Reply not found'
            for _ in instance:
                session.delete(_)
                session.commit()
        return ''

    @classmethod
    def vlan(cls, username, vlan):
        with sqla_session() as session:
            instance = session.query(Reply).filter(Reply.username == username).filter(Reply.attribute == 'Tunnel-Private-Group-Id').one_or_none()
            if not instance:
                return 'Reply not found'
            instance.value = vlan
        return ''
