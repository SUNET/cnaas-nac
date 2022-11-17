import fcntl
from datetime import datetime

import flock
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from cnaas_nac.tools.log import get_logger

logger = get_logger()


class JobError(Exception):
    def __init__(self, message):
        logger.debug(message)


class Scheduler(object):
    def __init__(self, nr_threads=1, lockfile="/tmp/cnaas_scheduler.lock"):
        self.__scheduler = BackgroundScheduler(
            executors={"default": ThreadPoolExecutor(nr_threads)},
            jobstores={"default": MemoryJobStore()},
            job_defaults={},
            timezone=utc,
        )

        self.lockfile = lockfile
        self.started = False
        self.job_id = 0
        self.jobstore = dict()

    def __lock(self):
        try:
            self.lockfp = open(self.lockfile, "w")
            fcntl.lockf(self.lockfp, flock.LOCK_EX)
        except IOError:
            return None

        return True

    def __unlock(self):
        if self.lockfp.writable():
            try:
                fcntl.lockf(self.lockfp, fcntl.LOCK_UN)
            except IOError:
                return False
            return True

        return False

    def __launcher(self, func, **kwargs):
        job_id = kwargs["job_id"]
        retval = None
        self.jobstore[job_id]["nr_runs"] += 1

        if "maxruns" in kwargs:
            if self.jobstore[job_id]["nr_runs"] >= kwargs["maxruns"]:
                if kwargs["maxruns"] != 0:
                    logger.debug(f"Reached max runs, removing job {job_id}.")
                    self.__scheduler.remove_job(job_id)
            del kwargs["maxruns"]
        del kwargs["job_id"]
        retval = func(**kwargs)

        return retval

    def start(self):
        if not self.__lock():
            logger.debug("Could not acquire lock")
            return None

        if self.started:
            logger.debug("Scheduler already started")
            return None

        self.started = True

        logger.debug("Starting scheduler")

        return self.__scheduler.start()

    def stop(self):
        return self.__scheduler.shutdown()

    def add(self, func, job_id="", comment="", timeout=120,
            interval=60, maxruns=1, starttime=None, **kwargs):
        if job_id == "":
            self.job_id += 1
            kwargs["job_id"] = str(self.job_id)
        else:
            if job_id in self.jobstore:
                raise JobError("Job already exists")
            kwargs["job_id"] = str(job_id)
        kwargs["func"] = func
        kwargs["maxruns"] = maxruns
        job_id = kwargs["job_id"]

        if not starttime:
            starttime = datetime.utcnow()

        self.jobstore[job_id] = {"nr_runs": 0}
        self.__scheduler.add_job(self.__launcher, id=job_id,
                                 trigger="interval",
                                 misfire_grace_time=timeout,
                                 seconds=interval,
                                 next_run_time=starttime,
                                 kwargs=kwargs)

        logger.debug(f"Scheduled recurrent job {job_id}")

        return self.job_id

    def delete_job(self, job_id):
        self.__scheduler.remove_job(job_id)
        del self.jobstore[job_id]
        logger.debug(f"Job {job_id} removed from scheduler.")

    def get_jobs(self):
        jobs = list()
        for key in self.jobstore.keys():
            jobs.append(key)
        return jobs


def test_job(**kwargs):
    logger.debug(kwargs)


if __name__ == "__main__":
    s = Scheduler()
    s.add_job(test_job, "test_1", seconds=2, maxruns=20, apa=132)

    while True:
        pass
