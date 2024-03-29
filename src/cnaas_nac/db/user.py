import enum
import ipaddress
from datetime import datetime, timedelta

from cnaas_nac.db.groups import Group
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.oui import DeviceOui
from cnaas_nac.db.reply import Reply
from cnaas_nac.db.session import sqla_session
from cnaas_nac.db.userinfo import UserInfo
from cnaas_nac.tools.ouis import ouis
from sqlalchemy import (Column, Integer, Unicode, UniqueConstraint, asc, desc,
                        func)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "radcheck"
    __table_args__ = (
        None,
        UniqueConstraint("id"),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(64), nullable=False, index=True, unique=True)
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
    def get(cls, username=""):
        result = []
        with sqla_session() as session:
            result = []
            if username == "":
                query = session.query(User).order_by("username")
            else:
                query = session.query(User).filter(
                    User.username == username).all()
            for _ in query:
                user = _.as_dict()
                user_dict = dict()
                user_dict["id"] = user["id"]
                user_dict["username"] = user["username"]
                user_dict["password"] = ""
                user_dict["op"] = user["op"]
                user_dict["attribute"] = user["attribute"]
                result.append(user_dict)
        return result

    @classmethod
    def add(cls, username, password):
        if cls.get(username) != []:
            return f"User {username} already exists"
        with sqla_session() as session:
            new_user = User()
            new_user.username = username
            new_user.attribute = "Cleartext-Password"
            new_user.value = password
            new_user.op = ""
            session.add(new_user)
        return ""

    @classmethod
    def enable(cls, username):
        with sqla_session() as session:
            user: User = (
                session.query(User)
                .filter(User.username == username)
                .order_by(User.id)
                .one_or_none()
            )
            if not user:
                return f"Username {username} not found"
            user.attribute = "Cleartext-Password"
            user.op = ":="
        return ""

    @classmethod
    def disable(cls, username):
        with sqla_session() as session:
            user: User = (
                session.query(User)
                .filter(User.username == username)
                .order_by(User.id)
                .one_or_none()
            )
            if not user:
                return f"Username {username} not found"
            user.attribute = "Cleartext-Password"
            user.op = ""
        return ""

    @classmethod
    def is_enabled(cls, username):
        enabled = False
        with sqla_session() as session:
            user: User = (
                session.query(User)
                .filter(User.username == username)
                .order_by(User.id)
                .one_or_none()
            )
            if not user:
                return None
            if user.op == ":=":
                enabled = True
        return enabled

    @classmethod
    def delete(cls, username):
        with sqla_session() as session:
            instance = session.query(User).filter(
                User.username == username).all()
            if not instance:
                return f"Username {username} not found"
            for _ in instance:
                session.delete(_)
                session.commit()
        return ""

    @classmethod
    def password(cls, username, password):
        with sqla_session() as session:
            user: User = (
                session.query(User)
                .filter(User.username == username)
                .order_by(User.id)
                .one_or_none()
            )
            if not user:
                return None
            user.value = password
        return ""


def get_users(field=None, condition="", order="", when=None, client_type=None,
              usernames_list=[], group=None):
    result = []

    if group is not None and group != "all":
        groupdict = Group.get(group)[0]
        field = groupdict["fieldname"]
        condition = groupdict["condition"]

    db_order = asc(User.username)
    db_field = User.username
    db_condition = "%{}%".format(condition.lower())
    db_when = datetime.now() - timedelta(days=3650)

    if when is not None:
        when_dict = {
            "hour": datetime.now() - timedelta(hours=1),
            "day": datetime.now() - timedelta(days=1),
            "week": datetime.now() - timedelta(days=7),
            "month": datetime.now() - timedelta(days=31),
            "year": datetime.now() - timedelta(days=365),
            "all": datetime.now() - timedelta(days=3650)
        }

        if when not in when_dict:
            db_when = datetime.now() - timedelta(days=3650)
        db_when = when_dict[when]

    if field is not None:
        field_dict = {
            "username": func.lower(User.username),
            "vlan": func.lower(Reply.value),
            "nasip": func.lower(NasPort.nas_ip_address),
            "nasport": func.lower(NasPort.nas_port_id),
            "reason": func.lower(UserInfo.reason),
            "comment": func.lower(UserInfo.comment)
        }

        if field not in field_dict:
            return []
        db_field = field_dict[field]

    if order != "":
        if "username" in order:
            db_order = (
                desc(User.username) if order.startswith(
                    "-") else asc(User.username)
            )
        elif "vlan" in order:
            db_order = desc(Reply.value) if order.startswith(
                "-") else asc(Reply.value)
        elif "reason" in order:
            db_order = (
                desc(UserInfo.reason) if order.startswith(
                    "-") else asc(UserInfo.reason)
            )
        elif "comment" in order:
            db_order = (
                desc(UserInfo.authdate)
                if order.startswith("-")
                else asc(UserInfo.authdate)
            )
        else:
            db_order = desc(User.username)

    userinfos = UserInfo.get(usernames=usernames_list)

    with sqla_session() as session:
        res = (
            session.query(User, Reply, NasPort, UserInfo)
            .filter(User.username == NasPort.username)
            .filter(Reply.username == User.username)
            .filter(Reply.attribute == "Tunnel-Private-Group-Id")
            .filter(UserInfo.username == User.username)
            .filter(db_field.like(db_condition))
            .filter(UserInfo.authdate > db_when)
            .order_by(db_order)
            .all()
        )

        for user, reply, nas_port, userinfo in res:
            if usernames_list != []:
                if user.username not in usernames_list:
                    continue

            res_dict = dict()
            res_dict["username"] = user.username
            res_dict["password"] = ""

            if user.op == ":=":
                res_dict["active"] = True
            else:
                res_dict["active"] = False
            res_dict["vlan"] = reply.value
            res_dict["nas_identifier"] = nas_port.nas_identifier
            res_dict["nas_port_id"] = nas_port.nas_port_id
            res_dict["nas_ip_address"] = nas_port.nas_ip_address
            res_dict["calling_station_id"] = nas_port.calling_station_id
            res_dict["called_station_id"] = nas_port.called_station_id
            res_dict["comment"] = userinfos[user.username]["comment"]
            res_dict["reason"] = userinfos[user.username]["reason"]
            res_dict["access_start"] = userinfos[user.username]["access_start"]
            res_dict["access_stop"] = userinfos[user.username]["access_stop"]
            res_dict["access_restricted"] = userinfos[user.username]["access_restricted"]
            res_dict["accepts"] = userinfos[user.username]["accepts"]
            res_dict["rejects"] = userinfos[user.username]["rejects"]
            res_dict["authdate"] = userinfos[user.username]["authdate"]

            user_oui = user.username[:8]

            try:
                res_dict["vendor"] = ouis[user_oui]
            except KeyError:
                res_dict["vendor"] = ""

            if "authdate" not in userinfos[user.username]:
                authdate = ""
            else:
                authdate = str(userinfos[user.username]["authdate"])

            res_dict["authdate"] = authdate
            result.append(res_dict)

    return result


def add_new_user(username, password, vlan, nas_ip_address,
                 nas_identifier, nas_port_id, calling_station_id,
                 called_station_id, reason="", comment="",
                 access_start=None, access_stop=None):

    op = ""

    if DeviceOui.exists(username):
        vlan = DeviceOui.get_vlan(username)
        op = ":="

    try:
        with sqla_session() as session:
            user = User(
                username=username,
                attribute="Cleartext-Password",
                value=password, op=op
            )
            tunnel_id = Reply(
                username=username,
                attribute="Tunnel-Private-Group-Id",
                op=":=",
                value=str(vlan)
            )
            tunnel_type = Reply(
                username=username,
                attribute="Tunnel-Type",
                op=":=",
                value="VLAN"
            )
            tunnel_medium = Reply(
                username=username,
                attribute="Tunnel-Medium-Type",
                op=":=",
                value="IEEE-802"
            )
            nas_port = NasPort(
                username=username,
                nas_ip_address=nas_ip_address,
                nas_identifier=nas_identifier,
                nas_port_id=nas_port_id,
                calling_station_id=calling_station_id,
                called_station_id=called_station_id
            )
            userinfo = UserInfo(
                username=username,
                reason=reason,
                comment=comment,
                authdate=datetime.utcnow(),
                access_start=access_start,
                access_stop=access_stop,
                accepts=0,
                rejects=0
            )

            session.add(user)
            session.add(tunnel_id)
            session.add(tunnel_type)
            session.add(tunnel_medium)
            session.add(nas_port)
            session.add(userinfo)
            session.commit()
    except Exception as e:
        return str(e)

    return ""


def delete_user(username):
    try:
        with sqla_session() as session:
            session.query(User).filter(User.username == username).delete()
            session.query(Reply).filter(Reply.username == username).delete()
            session.query(NasPort).filter(
                NasPort.username == username).delete()
            session.query(UserInfo).filter(
                UserInfo.username == username).delete()
            session.commit()
    except Exception as e:
        return str(e)

    return ""
