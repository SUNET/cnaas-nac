import time

from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User, PostAuth
from cnaas_nac.db.nas import NasPort


logger = get_logger()


ONE_MONTH = 2629800


def db_cleanup():
    users = User.get()
    pattern = '%Y-%m-%d %H:%M:%S.%f%z'

    logger.info('Cleaning up users...')

    for user in users:

        # Skip enabled users
        if user['op'] != '':
            logger.info('User {} active, skipping'.format(user['username']))
            continue

        post_auth = PostAuth.get_last_seen(username=user['username'])
        last_seen = str(post_auth[-1]['authdate'])

        last_seen_epoch = int(time.mktime(time.strptime(last_seen, pattern)))
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
