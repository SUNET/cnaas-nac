import sys
import getopt

from cnaas_nac.db.session import sqla_session
from cnaas_nac.db.user import User, Reply
from cnaas_nac.db.nas import NasPort

from cnaas_nac.tools.rad_db import edit_nas, edit_replies, edit_users, \
    get_connstrs, get_rows


def diff_rows(list_a: list, list_b: list) -> list:

    diff = []

    for x in list_a:
        del x['id']
    for x in list_b:
        del x['id']

    for item in list_a:
        if item not in list_b:
            diff.append(item)

    return diff


def rad_replicate(db_source: str, db_target: str, username: str, password: str,
                  table: object) -> None:

    connstr_source, connstr_target = get_connstrs(db_source, db_target,
                                                  username,
                                                  password)

    # Make sure to add any missing users on the target, also update any
    # diffing attribtes before going to the next step.
    source = get_rows(connstr_source, table=table)

    if table == User:
        edit_users(source, connstr_target)
    elif table == Reply:
        edit_replies(source, connstr_target)
    elif table == NasPort:
        edit_nas(source, connstr_target)

    # Remove all users that lives on the target but not on the source.
    target = get_rows(connstr_target, table=table)
    diff = diff_rows(target, source)

    if table == User:
        edit_users(diff, connstr_target, remove=True)
    elif table == Reply:
        edit_replies(diff, connstr_target, remove=True)
    elif table == NasPort:
        edit_nas(diff, connstr_target, remove=True)


def usage() -> None:

    print('Usage: -s <source addr> -t <target addr> -u <user> -p <passwd>')
    sys.exit(0)


def main(argv):

    source = None
    target = None
    username = None
    password = None

    try:
        opts, args = getopt.getopt(argv, 's:t:u:p:')
    except getopt.GetoptError as e:
        print(str(e))
        usage(argv)
    for opt, arg in opts:
        if opt == '-s':
            source = arg
        if opt == '-t':
            target = arg
        if opt == '-u':
            username = arg
        if opt == '-p':
            password = arg

    if source is None or target is None or username is None or password is None:
        usage()

    rad_replicate(source, target, username, password, User)
    rad_replicate(source, target, username, password, Reply)
    rad_replicate(source, target, username, password, NasPort)


if __name__ == '__main__':
    main(sys.argv[1:])
