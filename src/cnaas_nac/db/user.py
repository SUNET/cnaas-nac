from typing import Optional
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        None,
        UniqueConstraint('id'),
    )
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(128))
    password = Column(Unicode(128))
    description = Column(Unicode(255))
    active = Column(Boolean, default=False)
    attributes = Column(Unicode(1024))

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

    def get_user(self, username):
        if username in self.as_dict():
            return self.as_dict(['username'])
