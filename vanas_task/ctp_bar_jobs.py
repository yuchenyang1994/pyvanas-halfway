# -*- coding: utf-8 -*-
from ctp_bar_task import CtpTask
import redis
import logging
from pymongo import MongoClient
from conf.config import mongo_db, redis_db


redis_cli = redis.StrictRedis(host=redis_db['host'],port = redis_db['port'],db=redis_db['db'])
mongo_cli = MongoClient(mongo_db['host'],port=mongo_db['port'])

pyvanas_db = mongo_cli['pyvanas_test']
ctp_task = CtpTask(redis_cli,pyvanas_db)

def ctp_1_bar(sec_id):
    """一分钟任务

    :sec_id: TODO
    :returns: TODO

    """
    ctp_task.bar_task_time(sec_id,1)
    print('{sec_id}:success!'.format(sec_id=sec_id))

def ctp_5_bar(sec_id):
    """5分钟函数

    :sec_id: TODO
    :returns: TODO

    """
    ctp_task.bar_task_time(sec_id,5)
    logging.info('{sec_id}:success!'.format(sec_id=sec_id))

bar_jobs = {
    '1_bar':ctp_1_bar,
    '5_bar':ctp_5_bar
}

