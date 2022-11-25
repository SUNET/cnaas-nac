import os

from cnaas_nac.api.internal import app
from cnaas_nac.tools.cleanup import accounting_cleanup, users_cleanup
from cnaas_nac.tools.scheduler import Scheduler

os.environ['PYTHONPATH'] = os.getcwd()


def run_scheduler():
    scheduler = Scheduler()
    scheduler.add(users_cleanup, job_id="user cleanup",
                  interval=900, maxruns=0)
    scheduler.add(accounting_cleanup, job_id="accounting cleanup",
                  interval=3600, maxruns=0)
    scheduler.start()


def run_app():
    return app.app


if __name__ == '__main__':
    run_scheduler()
    run_app().run(debug=True, host='0.0.0.0', port=5002)
else:
    run_scheduler()
    cnaas_app = run_app()
