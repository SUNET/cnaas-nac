import enum
import ipaddress
import datetime

from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
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
    def get_last_seen(cls, usernames=[], last=True):
        users = dict()
        with sqla_session() as session:
            for username in usernames:
                postauth = session.query(PostAuth).filter(PostAuth.username ==
                                                          username).order_by(desc((PostAuth.id))).limit(1).one_or_none()
                last_seen = dict()
                if not postauth:
                    last_seen['authdate'] = ''
                    last_seen['reply'] = ''
                else:
                    last_seen['authdate'] = postauth.authdate
                    last_seen['reply'] = postauth.reply
                users[username] = last_seen
        return users
