import enum
import ipaddress
from datetime import datetime

from cnaas_nac.db.session import sqla_session
from sqlalchemy import Column, Integer, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Group(Base):
    __tablename__ = "radgroups"
    __table_args__ = (
        None,
        UniqueConstraint("id"),
        UniqueConstraint("groupname"),
    )
    id = Column(Integer, autoincrement=True, primary_key=True)
    groupname = Column(Text, nullable=False)
    fieldname = Column(Text, nullable=False)
    condition = Column(Text, nullable=False)

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
    def add(cls, groupname, fieldname, condition):
        with sqla_session() as session:
            group = Group()
            group.groupname = groupname
            group.fieldname = fieldname
            group.condition = condition
            session.add(group)

        return ""

    @classmethod
    def get(cls, groupname=None):
        groups = []
        with sqla_session() as session:
            if groupname:
                instance = (
                    session.query(Group)
                    .filter(Group.groupname == groupname)
                    .order_by("groupname")
                    .all()
                )
            else:
                instance = session.query(Group).order_by("groupname").all()
            if not instance:
                return []

            for group in instance:
                groups.append(group.as_dict())

        return groups

    @classmethod
    def get_data(cls, groupname):
        pass

    @classmethod
    def delete(cls, groupname):
        with sqla_session() as session:
            instance = (
                session.query(Group).filter(Group.groupname == groupname).all()
            )
            if not instance:
                return f"Group {groupname} not found"
            for group in instance:
                session.delete(group)
                session.commit()

        return ""
