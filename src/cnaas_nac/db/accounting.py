import datetime
import enum
import ipaddress

from cnaas_nac.db.session import sqla_session
from sqlalchemy import BigInteger, Column, DateTime, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Accounting(Base):
    __tablename__ = 'radacct'
    __table_args__ = (
        None,
        UniqueConstraint('radacctid'),
    )

    radacctid = Column(BigInteger, nullable=False, autoincrement=True,
                       primary_key=True)
    acctsessionid = Column(Text, nullable=False)
    acctuniqueid = Column(Text, nullable=False)
    username = Column(Text)
    groupname = Column(Text)
    realm = Column(Text)
    nasipaddress = Column(INET, nullable=False)
    nasportid = Column(Text)
    nasporttype = Column(Text)
    acctstarttime = Column(DateTime)
    acctupdatetime = Column(DateTime)
    acctstoptime = Column(DateTime)
    acctinterval = Column(BigInteger)
    acctsessiontime = Column(BigInteger)
    acctauthentic = Column(Text)
    connectinfo_start = Column(Text)
    connectinfo_stop = Column(Text)
    acctinputoctets = Column(BigInteger)
    acctoutputoctets = Column(BigInteger)
    calledstationid = Column(Text)
    callingstationid = Column(Text)
    acctterminatecause = Column(Text)
    servicetype = Column(Text)
    framedprotocol = Column(Text)
    framedipaddress = Column(INET)

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
    def get(cls):
        records = []
        with sqla_session() as session:
            items = session.query(Accounting).all()

            if not items:
                return records

            for item in items:
                records.append(item.as_dict())
        return records

    @classmethod
    def delete(cls, username, acctstoptime):
        with sqla_session() as session:
            res = session.query(Accounting).filter(Accounting.username == username).filter(
                Accounting.acctstoptime == acctstoptime).all()
            if not res or res == []:
                return
            for account in res:
                session.delete(account)
