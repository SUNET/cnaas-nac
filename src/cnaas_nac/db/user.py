import enum
import ipaddress
import datetime

from typing import Optional
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean
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
    nas_port = Column(Unicode(64), nullable=False)

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
    def user_get(cls, username=''):
        result = []
        with sqla_session() as session:
            result = []
            query = session.query(NasPort)
            for _ in query:
                user = _.as_dict()
                user_dict = dict()
                user_dict['id'] = user['id']
                user_dict['nas_port'] = user['nas_port']
                if username != '' and username != user['nas_port']:
                    continue
                result.append(user_dict)
        return result


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


class User(Base):
    __tablename__ = 'radcheck'
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
    def user_get(cls, username=''):
        result = []
        with sqla_session() as session:
            result = []
            query = session.query(User)
            for _ in query:
                user = _.as_dict()
                user_dict = dict()
                user_dict['id'] = user['id']
                user_dict['username'] = user['username']
                if username != '' and username != user['username']:
                    continue
                result.append(user_dict)
        return result

    @classmethod
    def reply_get(cls, username):
        result = []
        with sqla_session() as session:
            replymsg: Reply = session.query(Reply).filter(Reply.username ==
                                                          username).all()
            if replymsg is None:
                return result
            for _ in replymsg:
                result.append(_.as_dict())
        return result

    @classmethod
    def user_add(cls, username, password):
        if cls.user_get(username) != []:
            return 'User already exists'
        with sqla_session() as session:
            new_user = User()
            new_user.username = username
            new_user.attribute = 'Cleartext-Password'
            new_user.value = password
            new_user.op = ':='
            session.add(new_user)
        return ''

    @classmethod
    def user_enable(cls, username):
        with sqla_session() as session:
            user: User = session.query(User).filter(User.username ==
                                              username).one_or_none()
            if not user:
                return 'Username not found'
            user.attribute = 'Cleartext-Password'
            user.op = ':='
            user.value = user.username
        return ''

    @classmethod
    def user_disable(cls, username):
        with sqla_session() as session:
            user: User = session.query(User).filter(User.username ==
                                                    username).one_or_none()
            if not user:
                return 'Username not found'
            user.attribute = 'Auth-Type'
            user.op = ':='
            user.value = 'Reject'
        return ''

    @classmethod
    def reply_add(cls, username, vlan):
        if cls.reply_get(username) != []:
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
    def reply_del(cls, username):
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
    def user_del(cls, username):
        with sqla_session() as session:
            instance = session.query(User).filter(User.username ==
                                                  username).all()
            if not instance:
                return 'Username not found'
            for _ in instance:
                session.delete(_)
                session.commit()
        return ''
