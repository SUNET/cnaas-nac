import os
import time

from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User, UserInfo
from cnaas_nac.db.nas import NasPort


logger = get_logger()


ONE_MONTH = 2629800


def db_cleanup():
    if 'NO_CLEANUP' in os.environ:
        logger.info('Aborting cleanup.')
        return ''

    users = User.get()

    logger.info('Cleaning up users...')

    for user in users:
        username = user['username']

        # Skip enabled users
        if user['op'] != '':
            logger.info('User {} active, skipping'.format(username))
            continue

        userinfo = UserInfo.get([username])
        last_seen = userinfo[username]['authdate']

        if last_seen is None or last_seen == '':
            logger.info('No timestamp for user {}, skipping'.format(username))
            continue

        last_seen_epoch = int(last_seen.timestamp())
        current_epoch = int(time.time())

        if current_epoch - last_seen_epoch >= ONE_MONTH:
            logger.info('Removing user {}'.format(user['username']))
            User.delete(user['username'])
            User.reply_delete(user['username'])
            NasPort.delete(user['username'])

    return ''


if __name__ == '__main__':
    # Remove all INACTIVE users which are >30 days old.
    db_cleanup()
