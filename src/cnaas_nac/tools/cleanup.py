import os
import time

from cnaas_nac.db.session import get_sqlalchemy_conn_str
from cnaas_nac.db.user import delete_user, get_users
from cnaas_nac.tools.log import get_logger
from sqlalchemy import create_engine, inspect, text

logger = get_logger()
ONE_MONTH = 2629800


def users_cleanup():
    if "NO_CLEANUP" in os.environ:
        logger.info("Aborting cleanup.")
        return ""

    users = get_users()

    logger.info("Cleaning up users...")

    for user in users:
        username = user["username"]

        if "active" not in user or user["active"]:
            logger.info("User {} active, skipping".format(username))
            continue

        if "authdate" in user:
            authdate = user["authdate"]
        else:
            logger.info("No authdate for user {}, keeping".format(username))
            continue

        if authdate is None or authdate == "":
            logger.info("No timestamp for user {}, keeping".format(username))
            continue

        authdate_epoch = int(time.mktime(
            time.strptime(authdate, "%Y-%m-%d %H:%M:%S.%f")))
        current_epoch = int(time.time())

        if current_epoch - authdate_epoch >= ONE_MONTH:
            logger.info("Removing user {}, not enabled and not seen last month".format(
                user["username"]))
            delete_user(username)
        else:
            logger.info(
                "Keeping user {}, seen last month".format(user["username"]))

    return ""


def accounting_cleanup():
    logger.info("Cleaning up accounting...")

    if "NO_CLEANUP" in os.environ:
        logger.info("Aborting cleanup.")
        return ""

    engine = create_engine(get_sqlalchemy_conn_str())
    sqlstr = """DELETE FROM radacct WHERE acctstoptime < (now() - '30 days'::interval)"""

    with engine.connect() as connection:
        res = connection.execute(text(sqlstr))
        logger.info("Deleted {} rows from radacct".format(res.rowcount))

    logger.info("Accounting cleanup finished.")


def postauth_cleanup():
    logger.info("Cleaning up postauth...")

    if "NO_CLEANUP" in os.environ:
        logger.info("Aborting cleanup.")
        return ""

    engine = create_engine(get_sqlalchemy_conn_str())
    sqlstr = """DELETE FROM radpostauth WHERE authdate < (now() - '30 days'::interval)"""

    insp = inspect(engine)
    if "radpostauth" not in insp.get_table_names():
        logger.info("Table radpostauth does not exist, skipping")
        return

    with engine.connect() as connection:
        res = connection.execute(text(sqlstr))
        logger.info("Deleted {} rows from radpostauth".format(res.rowcount))

    logger.info("Postauth cleanup finished.")


if __name__ == "__main__":
    users_cleanup()
    accounting_cleanup()
    postauth_cleanup()
