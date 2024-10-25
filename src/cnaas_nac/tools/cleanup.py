import os
import time
from datetime import datetime

from cnaas_nac.db.accounting import Accounting
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.user import Reply, User, UserInfo
from cnaas_nac.tools.log import get_logger

logger = get_logger()
ONE_MONTH = 2629800


def users_cleanup():
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


def accounting_cleanup():
    removed_items = 0

    logger.info("Cleaning up accounting...")

    if "NO_CLEANUP" in os.environ:
        logger.info("Aborting cleanup.")
        return ""

    for account in Accounting.get():
        if "acctstoptime" in account:
            acctstoptime = account["acctstoptime"]
        else:
            continue

        if not acctstoptime:
            continue

        epoch_stop = round(datetime.strptime(
            acctstoptime, "%Y-%m-%d %H:%M:%S+00:00").timestamp())
        current_epoch = int(time.time())

        if current_epoch - epoch_stop >= ONE_MONTH:
            try:
                Accounting.delete(account["username"], account["acctstoptime"])
            except Exception:
                logger.info("Failed to remove account: {} {}".format(
                    account["username"], account["acctstoptime"]))
                continue
            removed_items += 1

    logger.info(f"Cleaned up {removed_items} items from radacct")


if __name__ == "__main__":
    users_cleanup()
    accounting_cleanup()
