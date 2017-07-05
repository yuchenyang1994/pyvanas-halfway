# -*- coding: utf-8 -*-
from pymongo import MongoClient
import redis
from vanas_api.vanas_ctp.ctp_app import CtpApp
from conf.config import mongo_db,redis_db,ctp_server

symbol_list = [('ni1701','ni'),('ru1701','ni'),('cu1612','cu'),
               ('zn1612','zn'),('al1612','al'),('rb1701','rb'),
               ('CF701','CF'),('SR701','SR'),('ZC701','ZC'),
               ('RM701','RM'),('TA701','TA'),('MA701','MA'),
               ('FG701','FG'),('y1701','y'),('p1701','p'),
               ('p1701','p'),('m1701','m'),('a1701','a'),
               ('jm1701','jm'),('l1701','l'),('v1701','v'),
               ('pp1701','pp'),('IF1611','IF'),('TF1612','TF')]

r = redis.StrictRedis(host=redis_db['host'],port=redis_db['port'],db=redis_db['db'])
mongo_cli = MongoClient(mongo_db['host'],port=mongo_db['port'])
pyvanas_db = mongo_cli[mongo_db['db']]
req_dict = {}
app = CtpApp(ctp_server['user_id'],
             ctp_server['passwd'],
             ctp_server['broker_id'],
             ctp_server['host'],
             req_dict,
             r,
             pyvanas_db
             )
app.connect()
app.login()
for sec_id,symbol in symbol_list:
    app.subscribe(sec_id,symbol)
app.run()


