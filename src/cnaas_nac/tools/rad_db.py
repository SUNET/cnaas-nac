from cnaas_nac.db.session import sqla_session
from cnaas_nac.db.user import User, Reply
from cnaas_nac.db.nas import NasPort


def get_connstrs(source: str, target: str, username: str,
                 password: str) -> tuple:

    connstr_source = 'postgresql://{}:{}@{}:5432/nac'.format(
        username, password, source)
    connstr_target = 'postgresql://{}:{}@{}:5432/nac'.format(
        username, password, target)

    return (connstr_source, connstr_target)


def get_rows(connstr: str, table: User) -> list:

    with sqla_session(connstr) as session:
        rows_list = []

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

            reply = session.query(Reply).filter(Reply.username == username).filter(Reply.attribute == attribute).one_or_none()

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
