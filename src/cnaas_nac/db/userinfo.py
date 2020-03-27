import enum
import ipaddress
import datetime

from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from cnaas_nac.db.session import sqla_session

Base = declarative_base()


class UserInfo(Base):
    __tablename__ = 'raduserinfo'
    __table_args__ = (
        None,
        UniqueConstraint('id'),
    )
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(64), nullable=False)
    comment = Column(Unicode(256))
    reason = Column(Unicode(256))
    authdate = Column(DateTime, default=datetime.datetime.utcnow,
                      onupdate=datetime.datetime.utcnow)

    @classmethod
    def add(cls, username, comment='', reason=''):
        with sqla_session() as session:
            res = session.query(UserInfo).filter(UserInfo.username == username).one_or_none()

            if res is not None:
                if comment != '':
                    res.comment = comment
                if reason != '':
                    res.reason = reason
            else:
                user = UserInfo()
                user.username = username
                user.reason = reason
                user.comment = comment
                session.add(user)

        return ''

    @classmethod
    def get(cls, usernames=[]):
        users = dict()
        with sqla_session() as session:
            for username in usernames:
                userinfo = session.query(UserInfo).filter(UserInfo.username ==
                                                          username).one_or_none()
                user_info = dict()
                if not userinfo:
                    user_info['comment'] = ''
                    user_info['reason'] = ''
                    user_info['authdate'] = ''
                else:
                    user_info['comment'] = userinfo.comment
                    user_info['reason'] = userinfo.reason
                    user_info['authdate'] = userinfo.authdate
                users[username] = user_info
        return users

    @classmethod
    def delete(cls, username):
        with sqla_session() as session:
            res = session.query(UserInfo).filter(UserInfo.username == username).one_or_none()
            if res is None:
                return 'User information not found'
            session.delete(res)

        return ''

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
