import enum
import ipaddress
import datetime

from typing import Optional
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean
from cnaas_nac.db.session import sqla_session


Base = declarative_base()


class PostAuth(Base):
    __tablename__ = 'radpostauth'
    __table_args__ = (
        None,
        UniqueConstraint('id'),
    )
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(64), nullable=False)
#    pass = Column(Unicode(64), nullable=False)
    reply = Column(Unicode(64), nullable=False)
#    CalledStationId = Column(Unicode(64), nullable=False)
#    CallingStationId = Column(Unicode(64), nullable=False)
    authdate = Column(DateTime, default=datetime.datetime.now)

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
    def get_last_seen(cls, username=None):
        res = []
        with sqla_session() as session:
            if username is not None:
                postauth: PostAuth = session.query(PostAuth).filter(PostAuth.username ==
                                                                    username).all()
            else:
                postauth: PostAuth = session.query(PostAuth).all()
            for auth in postauth:
                last_seen = dict()
                last_seen['username'] = auth.username
                last_seen['authdate'] = auth.authdate
                res.append(last_seen)
        return res


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
    def get(cls, username=''):
        result = []
        with sqla_session() as session:
            result = []
            if username == '':
                query = session.query(User).order_by('username')
            else:
                query = session.query(User).filter(User.username ==
                                                   username).all()
            for _ in query:
                user = _.as_dict()
                user_dict = dict()
                user_dict['id'] = user['id']
                user_dict['username'] = user['username']
                user_dict['op'] = user['op']
                user_dict['attribute'] = user['attribute']
                result.append(user_dict)
        return result

    @classmethod
    def reply_get(cls, username=None):
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
    def add(cls, username, password):
        if cls.get(username) != []:
            return 'User already exists'
        with sqla_session() as session:
            new_user = User()
            new_user.username = username
            new_user.attribute = 'Cleartext-Password'
            new_user.value = password
            new_user.op = ''
            session.add(new_user)
        return ''

    @classmethod
    def enable(cls, username):
        with sqla_session() as session:
            user: User = session.query(User).filter(User.username ==
                                              username).order_by(User.id).one_or_none()
            if not user:
                return 'Username not found'
            user.attribute = 'Cleartext-Password'
            user.op = ':='
        return ''

    @classmethod
    def disable(cls, username):
        with sqla_session() as session:
            user: User = session.query(User).filter(User.username ==
                                                    username).order_by(User.id).one_or_none()
            if not user:
                return 'Username not found'
            user.attribute = 'Cleartext-Password'
            user.op = ''
        return ''

    @classmethod
    def is_enabled(cls, username):
        enabled = False
        with sqla_session() as session:
            user: User = session.query(User).filter(User.username ==
                                                    username).order_by(User.id).one_or_none()
            if not user:
                return None
            if user.op == ':=':
                enabled = True
        return enabled

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
    def reply_delete(cls, username):
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
    def delete(cls, username):
        with sqla_session() as session:
            instance = session.query(User).filter(User.username ==
                                                  username).all()
            if not instance:
                return 'Username not found'
            for _ in instance:
                session.delete(_)
                session.commit()
        return ''

    @classmethod
    def is_enabled(cls, username):
        with sqla_session() as session:
            instance = session.query(User).filter(User.username ==
                                                  username).one_or_none()
            if not instance:
                return None
            if instance.op != ':=':
                return False
        return True

    @classmethod
    def reply_vlan(cls, username, vlan):
        with sqla_session() as session:
            instance = session.query(Reply).filter(Reply.username == username).filter(Reply.attribute == 'Tunnel-Private-Group-Id').one_or_none()
            if not instance:
                return 'Reply not found'
            instance.value = vlan
