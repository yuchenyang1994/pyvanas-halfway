# -*- coding: utf-8 -*-
from vanas_api.vanas_ib.ib_app import IbApp
from pymongo import MongoClient
import redis
from conf.config import mongo_db,redis_db,ib_server

req_dict = {}
tick_dict = {}
symbol_list = [#{'symbol':'YM','sec_type':'FUT','local_symbol':'YM   DEC 16','exchange':'ECBOT','currency':'USD'},
               #{'symbol':'ES','sec_type':'FUT','local_symbol':'ESZ6','exchange':'GLOBEX','currency':'USD'},
               #{'symbol':'NQ','sec_type':'FUT','local_symbol':'NQZ6','exchange':'GLOBEX','currency':'USD'},
               #{'symbol':'CL','sec_type':'FUT','local_symbol':'CLZ6','exchange':'NYMEX','currency':'USD'},
               #{'symbol':'NG','sec_type':'FUT','local_symbol':'NGX6','exchange':'NYMEX','currency':'USD'},
               #{'symbol':'GC','sec_type':'FUT','local_symbol':'GCZ6','exchange':'NYMEX','currency':'USD'},
               #{'symbol':'SI','sec_type':'FUT','local_symbol':'SIZ6','exchange':'NYMEX','currency':'USD'},
               #{'symbol':'HG','sec_type':'FUT','local_symbol':'SIZ6','exchange':'NYMEX','currency':'USD'},
               #{'symbol':'EUR','sec_type':'FUT','local_symbol':'6EZ6','exchange':'GLOBEX','currency':'USD'},
               #{'symbol':'GBP','sec_type':'FUT','local_symbol':'6BZ6','exchange':'GLOBEX','currency':'USD'},
               #{'symbol':'JPY','sec_type':'FUT','local_symbol':'6JZ6','exchange':'GLOBEX','currency':'USD'},
               #{'symbol':'AUD','sec_type':'FUT','local_symbol':'6AZ6','exchange':'GLOBEX','currency':'USD'},
               #{'symbol':'CAD','sec_type':'FUT','local_symbol':'6CZ6','exchange':'GLOBEX','currency':'USD'},
               #{'symbol':'NIKKEI225M','sec_type':'FUT','local_symbol':'161120019','exchange':'OSE.JPN','currency':'JPY'},
               #{'symbol':'K200','sec_type':'FUT','local_symbol':'016Z','exchange':'KSE','currency':'KRW'},
               #{'symbol':'HSI','sec_type':'FUT','local_symbol':'HSIV16','exchange':'HKFE','currency':'HKD'},
               #{'symbol':'HHI','sec_type':'FUT','local_symbol':'HHIV16','exchange':'HKFE','currency':'HKD'},
               {'symbol':'EUR','sec_type':'CASH','local_symbol':'','exchange':'IDEALPRO','currency':'USD'}
               ]
r = redis.StrictRedis(host = redis_db['host'],port=redis_db['port'],db=redis_db['db'])
mongo_cli = MongoClient(mongo_db['host'],port=mongo_db['port'])
pyvanas_db = mongo_cli[mongo_db['db']]
app = IbApp(ib_server['host'],ib_server['port'],ib_server['client_id'],req_dict,tick_dict,r,pyvanas_db)
app.econnect()
for symbol in symbol_list:
    app.subscribe(symbol['symbol'],symbol['currency'],symbol['sec_type'],symbol['exchange'],symbol['local_symbol'])

app.run()


