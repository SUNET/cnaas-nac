import enum
import ipaddress
import datetime

from sqlalchemy import Column, BigInteger, DateTime, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import INET


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
