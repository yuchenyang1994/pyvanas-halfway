# -*- coding: utf-8 -*-
from ib_bar_task import IbTask
from gevent import monkey;monkey.patch_all
import redis
import logging
from pymongo import MongoClient
from conf.config import mongo_db,redis_db

redis_cli = redis.StrictRedis(host=redis_db['host'],port = redis_db['port'],db=redis_db['db'])
mongo_cli = MongoClient(mongo_db['host'],port=mongo_db['port'])
pyvanas_db = mongo_cli['pyvanas_test']

ib_task = IbTask(redis_cli,pyvanas_db)
def ib_1_bar(sec_id):
    """TODO: Docstring for ib_1_bar.

    :sec_id: TODO
    :returns: TODO

    """
    ib_task.bar_task_time(sec_id,1)
    print('{sec_id}:success!'.format(sec_id=sec_id))

def ib_5_bar(sec_id):
    """5分钟线函数

    :sec_id: TODO
    :returns: TODO

    """
    ib_task.bar_task_time(sec_id,5)
    logging.info('{sec_id}:success!'.format(sec_id=sec_id))

bar_jobs = {
    '1_bar':ib_1_bar,
    '5_bar':ib_5_bar
}

