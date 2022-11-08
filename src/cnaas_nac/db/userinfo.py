import datetime
import enum
import ipaddress
import time

from cnaas_nac.db.session import sqla_session
from sqlalchemy import (BigInteger, Column, DateTime, Integer, Unicode,
                        UniqueConstraint, desc)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserInfo(Base):
    __tablename__ = "raduserinfo"
    __table_args__ = (
        None,
        UniqueConstraint("id"),
    )
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(64), nullable=False)
    comment = Column(Unicode(256))
    reason = Column(Unicode(256))
    authdate = Column(DateTime, default=datetime.datetime.utcnow)
    access_start = Column(DateTime, nullable=True)
    access_stop = Column(DateTime, nullable=True)
    accepts = Column(BigInteger, nullable=False)
    rejects = Column(BigInteger, nullable=False)

    @classmethod
    def add(cls, username, comment=None, reasonstr=None, auth=False,
            access_start=None, access_stop=None, reason=""):

        if access_start == "":
            access_start = None

        if access_stop == "":
            access_stop = None

        with sqla_session() as session:
            res = session.query(UserInfo).filter(
                UserInfo.username == username).one_or_none()

            if comment is None or comment == "":
                comment = "None"
            if reasonstr is None or reasonstr == "":
                reasonstr = "None"

            if res is not None:
                if not auth:
                    res.comment = comment
                else:
                    res.reason = reasonstr
                    res.authdate = datetime.datetime.utcnow()

                    if reason == "accept":
                        res.accepts += 1
                    if reason == "reject":
                        res.rejects += 1
            else:
                user = UserInfo()
                user.username = username
                user.reason = reasonstr
                user.comment = comment
                user.authdate = datetime.datetime.utcnow()
                user.access_start = access_start
                user.access_stop = access_stop
                user.accepts = 0
                user.rejects = 0

                session.add(user)

        return ""

    @classmethod
    def get(cls, usernames=[]):
        users = dict()
        with sqla_session() as session:
            for username in usernames:
                userinfo = session.query(UserInfo).filter(UserInfo.username ==
                                                          username).one_or_none()
                user_info = dict()
                access_restricted = False

                if userinfo:
                    time_now = int(round(time.time()))

                    if userinfo.access_start:
                        start_time = int(round(time.mktime(
                            userinfo.access_start.timetuple())))

                        if start_time > time_now:
                            access_restricted = True

                    if userinfo.access_stop:
                        stop_time = int(round(time.mktime(
                            userinfo.access_stop.timetuple())))

                        if stop_time < time_now:
                            access_restricted = True

                    user_info["comment"] = userinfo.comment
                    user_info["reason"] = userinfo.reason
                    user_info["authdate"] = userinfo.authdate
                    user_info["access_start"] = userinfo.access_start
                    user_info["access_stop"] = userinfo.access_stop
                    user_info["access_restricted"] = access_restricted
                    user_info["accepts"] = userinfo.accepts
                    user_info["rejects"] = userinfo.rejects

                users[username] = user_info
        return users

    @classmethod
    def get_stats(cls):
        stats = {
            "accepts": [],
            "rejects": [],
            "last_seen": []
        }

        with sqla_session() as session:
            userinfos = session.query(UserInfo).order_by(
                UserInfo.accepts.desc()).limit(10).all()

            for userinfo in userinfos:
                stats["accepts"].append({
                    "username": userinfo.username,
                    "accepts": userinfo.accepts
                })

        with sqla_session() as session:
            userinfos = session.query(UserInfo).order_by(
                UserInfo.rejects.desc()).limit(10).all()

            for userinfo in userinfos:
                stats["rejects"].append({
                    "username": userinfo.username,
                    "rejects": userinfo.rejects
                })

        with sqla_session() as session:
            userinfos = session.query(UserInfo).order_by(
                UserInfo.authdate.desc()).limit(10).all()

            for userinfo in userinfos:
                stats["last_seen"].append({
                    "username": userinfo.username,
                    "timestamp": userinfo.authdate,
                    "reason": userinfo.reason
                })

        return stats

    @classmethod
    def delete(cls, username):
        with sqla_session() as session:
            res = session.query(UserInfo).filter(
                UserInfo.username == username).one_or_none()
            if res is None:
                return f"User {username} information not found"
            session.delete(res)

        return ""

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
