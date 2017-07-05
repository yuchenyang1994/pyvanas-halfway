# -*- coding: utf-8 -*-
import redis
from pymongo import MongoClient
from vanas_server.vanas_rpc_server import VanasDataServer
from conf.config import mongo_db, redis_db
from threading import Thread


redis_cli = redis.StrictRedis(host=redis_db['host'],port = redis_db['port'],db=redis_db['db'])
mongo_cli = MongoClient(mongo_db['host'],port=mongo_db['port'])
pyvanas_db = mongo_cli['pyvanas_test']

NWORKERS = 1000
serv = VanasDataServer(('0.0.0.0', 5555),pyvanas_db,redis_cli)
for n in range(NWORKERS):
    t = Thread(target=serv._serv.serve_forever)
    t.daemon = True
    t.start()
serv._serv.serve_forever()







