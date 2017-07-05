# coding:utf-8

from vanas_md.vnctpmd import MdApi
from pymongo import MongoClient
import datetime
import json
import redis
import time


def print_dict(d):
    for key, value in d.items():
        print (key + ':' + str(value))


def simple_log(func):
    def wrapper(*args, **kw):
        print("")
        print(str(func.__name__))
        return func(*args, **kw)
    return wrapper




########################################################################

class CtpApp(object):

    """CTP连接器"""

    def __init__(self,user_id,passwd,brokerid,md_address,redis,mongodb):
        """TODO: to be defined1.

        :user_id: 用户
        :passwd: 密码
        :brokerid: broker_id
        :md_address: 地址

        """
        self.user_id = user_id
        self.passwd = passwd
        self.brokerid = brokerid
        self.md_address = md_address
        self.md_api = CtpMdApi(redis,mongodb) # 行情服务
        self.md_connected = False
        self.redis = redis

    def connect(self):
        """连接"""
        self.md_api.createFtdcMdApi('./vanas_con/')
        self.md_api.registerFront(self.md_address)
        self.md_connected = True
        self.md_api.init()
        time.sleep(0.5)

    def login(self):
        """登录服务器"""
        loginReq = {'UserID':self.user_id,
                    'Password':self.passwd,
                    'BrokerID':self.brokerid}
        reqid =  1
        self.md_api.reqUserLogin(loginReq,reqid)
        time.sleep(0.5)

    def subscribe(self, sec_id):
        """订阅行情"""
        self.md_api.subscribeMarketData(sec_id)
        cache_sec_id = 'ctp.{sec_id}'.format(sec_id=sec_id)
        self.redis.rpush('CTP_id_list',cache_sec_id)

    def run(self):
        """docstring for run"""
        while True:
            pass





class CtpMdApi(MdApi):

    """测试用实例"""

    #----------------------------------------------------------------------
    def __init__(self,redis,mongodb):
        """Constructor"""
        super(CtpMdApi, self).__init__()
        self.redis = redis
        self.mongodb = mongodb

    #----------------------------------------------------------------------
    def onFrontConnected(self):
        """服务器连接"""
        pass

    #----------------------------------------------------------------------
    def onFrontDisconnected(self, n):
        """服务器断开"""
        print(n)
    #----------------------------------------------------------------------

    def onHeartBeatWarning(self, n):
        """心跳报警"""
        print(n)

    #----------------------------------------------------------------------
    def onRspError(self, error, n, last):
        """错误"""
        print_dict(error)

    #----------------------------------------------------------------------
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        print_dict(data)
        print_dict(data)

    #----------------------------------------------------------------------
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        print_dict(error)
        print_dict(data)
    #----------------------------------------------------------------------

    def onRspSubMarketData(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(error)
        print_dict(data)
    #----------------------------------------------------------------------

    def onRspUnSubMarketData(self, data, error, n, last):
        """退订合约回报"""
        print_dict(error)
        print_dict(data)
    #----------------------------------------------------------------------

    def onRtnDepthMarketData(self, data):
        """行情推送"""
        tick_data = {}
        tick_data['symbol'] = data['InstrumentID']
        tick_data['exchange'] = data['ExchangeID'] if data['ExchangeID'] is not '' else "SHFE"
        tick_data['last_price'] = data['LastPrice']
        tick_data['volume'] = data['Volume']
        tick_data['open_Interest'] = data['OpenInterest']
        utc_time_src = '{date} {time}.{millise}'.format(date=data['TradingDay'],time=data['UpdateTime'],millise=data['UpdateMillisec'])
        utc_time = datetime.datetime.strptime(utc_time_src,'%Y%m%d %H:%M:%S.%f')
        tick_data['utc_time'] = utc_time
        tick_data['open_price'] = data['OpenPrice']
        tick_data['high_price'] = data['HighestPrice']
        tick_data['low_price'] = data['LowestPrice']
        tick_data['pre_close_price'] = data['PreClosePrice']
        tick_data['upper_limit'] = data['UpperLimitPrice']
        tick_data['lower_limit'] = data['LowerLimitPrice']

        # 行情档
        tick_data['bid_price'] = data['BidPrice1']
        tick_data['bid_volume'] = data['BidVolume1']
        tick_data['ask_price'] = data['AskPrice1']
        tick_data['ask_volume'] = data['AskVolume1']
        # sec_id
        sec_id = tick_data['symbol']
        cache_sec_id = 'ctp.{sec_id}'.format(sec_id=sec_id)
        # 将数据存入mongodb
        tick_collection = self.mongodb[cache_sec_id]
        tick_collection.insert(tick_data)
        # 发布tick级别的数据
        del tick_data['_id']
        tick_data['utc_time'] = utc_time_src
        channel = '{sec_id}.{rate}'.format(sec_id=sec_id,rate='tick')
        self.redis.publish(channel,json.dumps(tick_data))
        print(tick_data)


    #----------------------------------------------------------------------
    def onRspSubForQuoteRsp(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(error)
        print_dict(data)
    #----------------------------------------------------------------------

    def onRspUnSubForQuoteRsp(self, data, error, n, last):
        """退订合约回报"""
        pass

    #----------------------------------------------------------------------
    def onRtnForQuoteRsp(self, data):
        """行情推送"""
        pass

if __name__ == "__main__":
    r = redis.StrictRedis(host='127.0.0.1',port=6379,db=0)
    mongo_cli = MongoClient('139.196.6.151',port=26666)
    pyvanas_db = mongo_cli['pyvanas_test']
    app = CtpApp('069586','940304','9999','tcp://180.168.146.187:10010',r,pyvanas_db)
    app.connect()
    app.login()
    app.subscribe('cu1701')
    app.run()


