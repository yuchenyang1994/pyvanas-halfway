# -*- coding: utf-8 -*-

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from bson import ObjectId
import json
import redis
from pymongo import MongoClient
import datetime

class VanasDataServer(object):

    """vanas_data_server"""
    _rpc_methods_ = ['get_data','send_status']

    def __init__(self,address,pyvanas_db,redis):
        """TODO: to be defined1. """
        self._serv = SimpleXMLRPCServer(address,allow_none = True)
        self._db = pyvanas_db
        self._redis = redis
        for name in self._rpc_methods_:
            self._serv.register_function(getattr(self,name))

    def get_data(self,symbol,start_time,end_time,user_id):
        """docstring for get_data"""
        user_info = self._db['user']
        user = user_info.find_one({'_id':ObjectId(user_id)})
        start_utc_time = datetime.datetime.strptime(start_time,"%Y-%m-%d %H:%M")
        end_utc_time = datetime.datetime.strptime(end_time,"%Y-%m-%d %H:%M")
        if user:
            collections_name = '{symbol}_1_bar'.format(symbol = symbol)
            collections = self._db[collections_name]
            data = collections.find({'start_utc_time':{"$gte":start_utc_time,"$lt":end_utc_time}},{"_id":0}).sort('start_utc_time')
            bar_data = []
            for bar in data:
                bar['start_utc_time'] = str(bar['start_utc_time'])
                bar['end_utc_time'] = str(bar['end_utc_time'])
                bar_data.append(bar)
            return bar_data
        else:
            return "you must be registed"

    def send_status(self,data,user_id):
        """发送数据"""
        user_info = self._db['user']
        user = user_info.find_one({'_id':ObjectId(user_id)})
        if user:
            channel_name = 'user.{user_name}'.format(user_name=user['username'])
            self._redis.publish(channel_name,json.dumps(data))
            return 'ok'
        else:
            return "you must be registed"



if __name__ == "__main__":

    mongo_cli = MongoClient('139.196.6.151',26666)
    pyvanas_db = mongo_cli['pyvanas_test']
    redis_cli = redis.StrictRedis(host='127.0.0.1',port = 6379)
    vanas_server = VanasDataServer(('localhost',5555),pyvanas_db,redis_cli)
    vanas_server._serv.serve_forever()



