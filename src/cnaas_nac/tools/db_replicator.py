import sys
import getopt

from cnaas_nac.db.session import sqla_session
from cnaas_nac.db.user import User, Reply
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.accounting import Accounting
from cnaas_nac.tools.log import get_logger

from cnaas_nac.tools.rad_db import edit_nas, edit_replies, edit_users, \
    get_connstrs, get_rows, copy_accounting


logger = get_logger()


def diff_rows(list_a: list, list_b: list) -> list:

    diff = []

    for x in list_a:
        if 'id' in x:
            del x['id']
    for x in list_b:
        if 'id' in x:
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
        logger.info('Editing users, correcting values...')
        edit_users(source, connstr_target)
    elif table == Reply:
        logger.info('Editing replies, correcting values...')
        edit_replies(source, connstr_target)
    elif table == NasPort:
        logger.info('Editing ports, correcting values...')
        edit_nas(source, connstr_target)
    elif table == Accounting:
        logger.info('Copying accounting data...')
        copy_accounting(source, connstr_target)

    # Remove all users that lives on the target but not on the source. We will
    # not remove any accounting data, only copy it.
    target = get_rows(connstr_target, table=table)
    diff = diff_rows(target, source)

    if table == User:
        logger.info('Revmoing users from target that not exist on source...')
        edit_users(diff, connstr_target, remove=True)
    elif table == Reply:
        logger.info('Revmoing replies from target that not exist on source...')
        edit_replies(diff, connstr_target, remove=True)
    elif table == NasPort:
        logger.info('Revmoing ports from target that not exist on source...')
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

    logger.info('Replicating users...')
    rad_replicate(source, target, username, password, User)
    logger.info('Replicating replies...')
    rad_replicate(source, target, username, password, Reply)
    logger.info('Replicating ports...')
    rad_replicate(source, target, username, password, NasPort)
    logger.info('Replicating accounting...')
    rad_replicate(source, target, username, password, Accounting)
    logger.info('Done.')


if __name__ == '__main__':
    main(sys.argv[1:])
