# -*- coding: utf-8 -*-
import gevent
from gevent import monkey;monkey.patch_all()
from gevent.pool import Pool
from vanas_task.ib_bar_jobs import bar_jobs
import sys
import schedule
import time
from vanas_task.ib_bar_jobs import redis_cli


job = sys.argv[1]
job_rate = sys.argv[2]
pool = Pool(1000)


def start_jobs():
    """TODO: Docstring for start_jobs.
    :returns: TODO

    """
    sec_id_list = redis_cli.smembers('IB_id_set')
    pool.map(bar_jobs[job],list(sec_id_list))

schedule.every(int(job_rate)).minutes.do(start_jobs)
while True:
    schedule.run_pending()
    time.sleep(1)


