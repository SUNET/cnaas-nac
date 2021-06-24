from cnaas_nac.db.userinfo import UserInfo
from cnaas_nac.db.reply import Reply
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.session import sqla_session
from sqlalchemy import Boolean, desc, asc
from sqlalchemy.ext.declarative import declarative_base
import enum
import ipaddress
from datetime import datetime, timedelta

from typing import Optional
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, DateTime, \
    func


Base = declarative_base()


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
            elif issubclass(value.__class__, datetime):
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


def get_users(field=None, condition='', order='', when=None):
    result = []

    db_order = asc(User.username)
    db_field = User.username
    db_condition = '%{}%'.format(condition)
    db_when = datetime.now() - timedelta(days=3650)

    if when is not None:
        if when == 'hour':
            db_when = datetime.now() - timedelta(hours=1)
        elif when == 'day':
            db_when = datetime.now() - timedelta(days=1)
        elif when == 'week':
            db_when = datetime.now() - timedelta(days=7)
        elif when == 'month':
            db_when = datetime.now() - timedelta(days=31)
        elif when == 'year':
            db_when = datetime.now() - timedelta(days=365)
        elif when == 'all':
            db_when = datetime.now() - timedelta(days=3650)
        else:
            db_when = datetime.now() - timedelta(days=3650)

    if field is not None:
        if field == 'username':
            db_field = User.username
        elif field == 'vlan':
            db_field = Reply.value
        elif field == 'nasip':
            db_field = NasPort.nas_ip_address
        elif field == 'nasport':
            db_field = NasPort.nas_port_id
        elif field == 'reason':
            db_field = UserInfo.reason
        elif field == 'comment':
            db_field = UserInfo.comment
        else:
            return []

    if order != '':
        if 'username' in order:
            db_order = desc(User.username) if order.startswith(
                '-') else asc(User.username)
        elif 'vlan' in order:
            db_order = desc(Reply.value) if order.startswith(
                '-') else asc(Reply.value)
        elif 'reason' in order:
            db_order = desc(UserInfo.reason) if order.startswith(
                '-') else asc(UserInfo.reason)
        elif 'comment' in order:
            db_order = desc(UserInfo.authdate) if order.startswith(
                '-') else asc(UserInfo.authdate)
        else:
            db_order = desc(User.username)

    with sqla_session() as session:
        res = session.query(User, Reply, NasPort, UserInfo).filter(User.username == NasPort.username).filter(Reply.username == User.username).filter(
            Reply.attribute == 'Tunnel-Private-Group-Id').filter(UserInfo.username == User.username).filter(db_field.like(db_condition)).filter(UserInfo.authdate > db_when).order_by(db_order).all()

        usernames = []
        for user, reply, nas_port, userinfo in res:
            usernames.append(user.username)

        userinfos = UserInfo.get(usernames=usernames)
        for user, reply, nas_port, userinfo in res:
            if usernames != []:
                if user.username not in usernames:
                    continue
            res_dict = dict()
            res_dict['username'] = user.username

            if user.op == ':=':
                res_dict['active'] = True
            else:
                res_dict['active'] = False
            res_dict['vlan'] = reply.value
            res_dict['nas_identifier'] = nas_port.nas_identifier
            res_dict['nas_port_id'] = nas_port.nas_port_id
            res_dict['nas_ip_address'] = nas_port.nas_ip_address
            res_dict['calling_station_id'] = nas_port.calling_station_id
            res_dict['called_station_id'] = nas_port.called_station_id
            res_dict['comment'] = userinfos[user.username]['comment']
            res_dict['reason'] = userinfos[user.username]['reason']

            if 'authdate' not in userinfos[user.username]:
                authdate = ''
            else:
                authdate = str(userinfos[user.username]['authdate'])

            res_dict['authdate'] = authdate
            result.append(res_dict)

    return result
