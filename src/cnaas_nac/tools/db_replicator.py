import os
import sys
import getopt

from cnaas_nac.db.session import sqla_session
from cnaas_nac.db.user import User
from cnaas_nac.db.reply import Reply
from cnaas_nac.db.userinfo import UserInfo
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.accounting import Accounting
from cnaas_nac.tools.log import get_logger

from cnaas_nac.tools.rad_db import edit_nas, edit_replies, edit_users, \
    get_connstrs, get_rows, copy_accounting, edit_userinfo


logger = get_logger()


def diff_rows(list_a: list, list_b: list) -> list:

    diff = []

    for x in list_a:
        if 'id' in x:
            del x['id']
        if 'authdate' in x:
            del x['authdate']
    for x in list_b:
        if 'id' in x:
            del x['id']
        if 'authdate' in x:
            del x['authdate']

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
    elif table == UserInfo:
        logger.info('Copying userinfo data...')
        edit_userinfo(source, connstr_target)

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
    elif table == UserInfo:
        logger.info('Removing userinfo from target that not exist on source...')
        edit_userinfo(diff, connstr_target, remove=True)


def usage() -> None:
    print('Usage: -s <source addr> -t <target addr> -u <user> -p <passwd>\n')
    print('Or set the environment variables NAC_REPLICATE_PASSWORD')
    print('NAC_REPLICATE_SOURCE, NAC_REPLICATE_TARGET, NAC_REPLICATE_USERNAME')
    print('and use the flag -e.')
    sys.exit(0)


def env_vars() -> tuple:
    try:
        source = os.environ['NAC_REPLICATE_SOURCE']
        target = os.environ['NAC_REPLICATE_TARGET']
        username = os.environ['NAC_REPLICATE_USERNAME']
        password = os.environ['NAC_REPLICATE_PASSWORD']
    except Exception:
        return None, None, None, None
    return source, target, username, password


def main(argv):

    source = None
    target = None
    username = None
    password = None
    envvar = False

    try:
        opts, args = getopt.getopt(argv, 's:t:u:p:e')
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
        if opt == '-e':
            envvar = True
        if opt == '-h':
            usage()

    if envvar:
        source, target, username, password = env_vars()

    if None in (source, target, username, password):
        sys.exit(-1)

    try:
        logger.info('Starting DB replication from {} to {}'.format(source, target))

        logger.info('Replicating users...')
        rad_replicate(source, target, username, password, User)
        logger.info('Replicating replies...')
        rad_replicate(source, target, username, password, Reply)
        logger.info('Replicating ports...')
        rad_replicate(source, target, username, password, NasPort)
        logger.info('Replicating userinfo...')
        rad_replicate(source, target, username, password, UserInfo)

        # Do not replicate accounting data now, it takes too long time.
        # logger.info('Replicating accounting...')
        # rad_replicate(source, target, username, password, Accounting)

        logger.info('Replication finished successfully')
    except Exception as e:
        logger.warning('Replication failed with exception: ' + str(e))


if __name__ == '__main__':
    main(sys.argv[1:])
