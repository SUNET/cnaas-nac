from cnaas_nac.db.session import sqla_session
from cnaas_nac.db.user import User, Reply, UserInfo
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.accounting import Accounting


def get_connstrs(source: str, target: str, username: str,
                 password: str) -> tuple:

    connstr_source = 'postgresql://{}:{}@{}:5432/nac'.format(
        username, password, source)
    connstr_target = 'postgresql://{}:{}@{}:5432/nac'.format(
        username, password, target)

    return (connstr_source, connstr_target)


def get_rows(connstr: str, table: object) -> list:

    with sqla_session(connstr) as session:
        rows_list = []

        if table == Accounting:
            rows = session.query(table).order_by(table.radacctid).all()
        else:
            rows = session.query(table).order_by(table.id).all()
        for row in rows:
            rows_list.append(row.as_dict())
    return rows_list


def edit_users(diff, connstr, remove=False):

    if diff is None:
        return

    with sqla_session(connstr) as session:
        for diff_user in diff:
            username = diff_user['username']
            attribute = diff_user['attribute']
            op = diff_user['op']
            value = diff_user['value']

            user = session.query(User).filter(User.username ==
                                              username).one_or_none()

            if remove and user is not None:
                print('Removing user {}'.format(username))
                session.delete(user)
            elif user is None and not remove:
                print('Adding user {}'.format(username))
                new_user = User()
                new_user.username = username
                new_user.attribute = attribute
                new_user.op = op
                new_user.value = value
                session.add(new_user)
            elif user is not None:
                if attribute != user.attribute or op != user.op or value != user.value:
                    print('Changing user {}'.format(username))
                    user.attribute = attribute
                    user.op = op
                    user.value = value
            session.commit()


def edit_replies(diff, connstr, remove=False):

    if diff is None:
        return

    with sqla_session(connstr) as session:
        for diff_user in diff:
            username = diff_user['username']
            attribute = diff_user['attribute']
            op = diff_user['op']
            value = diff_user['value']

            reply = session.query(Reply).filter(Reply.username == username).filter(
                Reply.attribute == attribute).one_or_none()

            if remove and reply is not None:
                print('Removing reply {}'.format(username))
                session.delete(reply)
            elif reply is None and not remove:
                print('Adding reply {}'.format(username))
                new_reply = Reply()
                new_reply.username = username
                new_reply.attribute = attribute
                new_reply.op = op
                new_reply.value = value
                session.add(new_reply)
            elif reply is not None:
                if attribute != reply.attribute or op != reply.op or value != reply.value:
                    print('Changing reply {}'.format(username))
                    reply.attribute = attribute
                    reply.op = op
                    reply.value = value
            session.commit()


def edit_nas(nas_diff, connstr, table=NasPort, remove=False):

    if nas_diff is None:
        return

    with sqla_session(connstr) as session:
        for diff_user in nas_diff:
            username = diff_user['username']
            nas_identifier = diff_user['nas_identifier']
            nas_port_id = diff_user['nas_port_id']
            nas_ip_address = diff_user['nas_ip_address']
            calling_station_id = diff_user['calling_station_id']
            called_station_id = diff_user['called_station_id']

            nas = session.query(table).filter(NasPort.username ==
                                              username).one_or_none()

            if remove and nas is not None:
                print('Removing user {}'.format(username))
                session.delete(nas)
            elif nas is None and not remove:
                print('Adding user {}'.format(username))
                new_nas = table()
                new_nas.username = username
                new_nas.nas_identifier = nas_identifier
                new_nas.nas_port_id = nas_port_id
                new_nas.nas_ip_address = nas_ip_address
                new_nas.calling_station_id = calling_station_id
                new_nas.called_station_id = called_station_id
                session.add(new_nas)
            elif nas is not None:
                if nas_identifier != nas.nas_identifier or nas_port_id != nas.nas_port_id or nas_ip_address != nas.nas_ip_address or calling_station_id != nas.calling_station_id or called_station_id != nas.called_station_id:
                    print('Changing nas {}'.format(username))
                    nas.nas_identifier = nas_identifier
                    nas.nas_port_id = nas_port_id
                    nas.nas_ip_address = nas_ip_address
                    nas.calling_station_id = calling_station_id
                    nas.called_station_id = called_station_id
            session.commit()


def copy_accounting(diffs, connstr, table=Accounting):

    if diffs is None or diffs == []:
        return

    with sqla_session(connstr) as session:
        for diff in diffs:
            if diff is None:
                continue
            radacctid = diff['radacctid']
            acctsessionid = diff['acctsessionid']
            acctuniqueid = diff['acctuniqueid']
            username = diff['username']
            groupname = diff['groupname']
            realm = diff['realm']
            nasipaddress = diff['nasipaddress']
            nasportid = diff['nasportid']
            nasporttype = diff['nasporttype']
            acctstarttime = diff['acctstarttime']
            acctupdatetime = diff['acctupdatetime']
            acctstoptime = diff['acctstoptime']
            acctinterval = diff['acctinterval']
            acctsessiontime = diff['acctsessiontime']
            acctauthentic = diff['acctauthentic']
            connectinfo_start = diff['connectinfo_start']
            connectinfo_stop = diff['connectinfo_stop']
            acctinputoctets = diff['acctinputoctets']
            acctoutputoctets = diff['acctoutputoctets']
            calledstationid = diff['calledstationid']
            callingstationid = diff['callingstationid']
            acctterminatecause = diff['acctterminatecause']
            servicetype = diff['servicetype']
            framedprotocol = diff['framedprotocol']
            framedipaddress = diff['framedipaddress']

            acct = session.query(table).filter(Accounting.acctuniqueid ==
                                               acctuniqueid).one_or_none()

            if acct is None:
                print('Adding accounting session {}'.format(acctsessionid))
                new_acct = table()
                new_acct.radacctid = radacctid
                new_acct.acctsessionid = acctsessionid
                new_acct.acctuniqueid = acctuniqueid
                new_acct.username = username
                new_acct.groupname = groupname
                new_acct.realm = realm
                new_acct.nasipaddress = nasipaddress
                new_acct.nasportid = nasportid
                new_acct.nasporttype = nasporttype
                new_acct.acctstarttime = acctstarttime
                new_acct.acctupdatetime = acctupdatetime
                new_acct.acctstoptime = acctstoptime
                new_acct.acctinterval = acctinterval
                new_acct.acctsessiontime = acctsessiontime
                new_acct.acctauthentic = acctauthentic
                new_acct.connectinfo_start = connectinfo_start
                new_acct.connectinfo_stop = connectinfo_stop
                new_acct.acctinputoctets = acctinputoctets
                new_acct.acctoutputoctets = acctoutputoctets
                new_acct.calledstationid = calledstationid
                new_acct.callingstationid = callingstationid
                new_acct.acctterminatecause = acctterminatecause
                new_acct.servicetype = servicetype
                new_acct.framedprotocol = framedprotocol
                new_acct.framedipaddress = framedipaddress
                session.add(new_acct)
            session.commit()


def edit_userinfo(userinfo_diff, connstr, table=UserInfo, remove=False):

    if userinfo_diff is None:
        return

    with sqla_session(connstr) as session:
        for diff_user in userinfo_diff:
            username = diff_user['username']
            comment = diff_user['comment']
            reason = diff_user['reason']

            if 'authdate' in diff_user:
                authdate = diff_user['authdate']

            userinfo = session.query(table).filter(UserInfo.username ==
                                                   username).one_or_none()

            if remove and userinfo is not None:
                print('Removing user {}'.format(username))
                session.delete(userinfo)
            elif userinfo is None and not remove:
                print('Adding user {}'.format(username))
                new_userinfo = table()
                new_userinfo.username = username
                new_userinfo.comment = comment
                new_userinfo.reason = reason
                new_userinfo.authdate = authdate
                session.add(new_userinfo)
            elif userinfo is not None:
                if comment != userinfo.comment or reason != userinfo.reason:
                    print('Changing userinfo {}'.format(username))
                    userinfo.comment = comment
                    userinfo.reason = reason
                    userinfo.authdate = authdate
            session.commit()
