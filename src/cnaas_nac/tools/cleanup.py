import os
import time

from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.user import Reply, User, UserInfo
from cnaas_nac.tools.log import get_logger

logger = get_logger()


ONE_MONTH = 2629800


def db_cleanup():
    if "NO_CLEANUP" in os.environ:
        logger.info("Aborting cleanup.")
        return ""

    users = User.get()

    logger.info("Cleaning up users...")

    for user in users:
        username = user["username"]

        # Skip enabled users
        if user["op"] != "":
            logger.info("User {} active, skipping".format(username))
            continue

        userinfo = UserInfo.get([username])
        authdate = userinfo[username]["authdate"]

        if authdate is None or authdate == "":
            logger.info("No timestamp for user {}, skipping".format(username))
            continue

        authdate_epoch = int(authdate.timestamp())
        current_epoch = int(time.time())

        if current_epoch - authdate_epoch >= ONE_MONTH:
            logger.info("Removing user {}".format(user["username"]))
            User.delete(user["username"])
            Reply.delete(user["username"])
            NasPort.delete(user["username"])
        else:
            logger.info("Keeping user {}".format(user["username"]))

    return ""


if __name__ == "__main__":
    # Remove all INACTIVE users which are >30 days old.
    db_cleanup()
