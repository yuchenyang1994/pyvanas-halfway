# -*- coding: utf-8 -*-

from ib.ext.Contract import Contract
from ib.ext.EWrapper import EWrapper
from ib.ext.EClientSocket import EClientSocket
from tick_type import tick_field
import datetime
import copy
import logging




class IbApp(object):

    """IB链接器"""

    def __init__(self,host,port,client_id,req_dict,tick_dict,redis,mongo_db):
        """
        TODO: 不应该维护一个巨大的类，可以考虑使用混合模式来管理这个类
        :host:地址
        :port:接口
        :client_id:这个可以随便写一个,int
        :req_id:请求id
        :redis:redis实例
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.warpper = IbTestWrapper(req_dict,tick_dict,mongo_db)
        self.connection = EClientSocket(self.warpper)
        self.req_id = 0
        self.req_dict = req_dict
        self.tick_dict = tick_dict
        self.redis = redis

    def econnect(self):
        """docstring for connect"""
        # 连接TWS
        self.connection.eConnect(self.host,self.port,self.client_id)

    def subscribe(self,m_symbol,currency,m_sec_type,m_exchange,m_local_symbol):
        """
        :return: 返回req_id和合约代码信息返回,好做好映射，
        """
        contract = Contract()
        contract.m_symbol = m_symbol # 底层资产的代码 PS:CL
        contract.m_currency = currency # 币种 PS:USD
        contract.m_secType = m_sec_type # 证券类型 PS:FUT
        contract.m_exchange = m_exchange # 交易所NYMEX
        contract.m_localSymbol = m_local_symbol #合约代码
        self.req_id += 1
        self.connection.reqMktData(self.req_id,contract,'',False) # 订阅
        logging.info("正在订阅:"+m_local_symbol)
        self.tick_dict[self.req_id] = {} # 初始化Tick的数据
        #cache_symbol
        cache_symbol = m_local_symbol if ' ' not in m_local_symbol else m_local_symbol.replace(' ','_')

        # 将合约ID存入Redis以后使用
        sec_id = 'ib.{m_exchange}.{m_local_symbol}'.format(m_exchange = m_exchange,m_local_symbol = cache_symbol if not m_local_symbol == '' else m_symbol)
        self.redis.sadd('IB_id_set',sec_id)


        # 将订阅合约信息保存在字典中
        self.req_dict[self.req_id]={'symbol':m_symbol,'currency':currency,'sec_type':m_sec_type,
                               'exchange':m_exchange,'local_symbol':cache_symbol}
    def query_account(self,acc_code):
        """
        docstring for query_account
        查询账户信息
        似乎是主动推送
        """
        self.connection.reqAccountUpdates(1, acc_code)

    def run(self):
        """运行"""
        while True:
            pass


class IbTestWrapper(EWrapper):

    """
    Ib回调函数
    """

    def __init__(self,req_dict,tick_data,mongo_db):
        """
        :req_dict:保存请求数据的字典
        """
        super(IbTestWrapper,self).__init__()
        self.req_dict = req_dict
        self.tick_data = tick_data
        self.mongo_db = mongo_db
    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """
        :推送数据(价格相关
        """
        if field in tick_field:
            # 将合约信息取出
            req_info = self.req_dict[tickerId]
            # 合约ID
            sec_id = "ib.{exchange}.{local_symbol}".format(exchange = req_info['exchange'],
                                                        local_symbol = req_info['local_symbol'] if not req_info['local_symbol'] == '' else req_info['symbol'])
            # 取出映射的数据类型
            tick_key = tick_field[field]
            # 取出缓存中保存的数据
            data = self.tick_data[tickerId]
            # 如果买卖最后尺寸和价格存在，那么拍摄快照
            if 'bid_volume' and 'bid_price' and 'ask_price' and 'ask_volume' \
                    and 'last_price' and 'last_volume' in data:
                data[tick_key] = price
                utc_time = datetime.datetime.now()
                data['utc_time'] = utc_time
                copy_data = copy.deepcopy(data)
                # 存入数据
                if 'volume' and 'high_price' and 'low_price' and 'pre_close_price' in data:
                    tick_collection = self.mongo_db[sec_id]
                    tick_collection.insert(copy_data)
                data['last_volume'] = 0
                logging.info("成功获取数据:" + sec_id)
                print(sec_id)

            # 否则等数据写入后再说
            else:
                #将合约信息取出
                req_info = self.req_dict[tickerId]
                data[tick_key] = price
                #将合约信息写入
                data['exchange'] = req_info['exchange']
                data['sec_id'] = "{exchange}.{local_symbol}".format(exchange = req_info['exchange'],
                                                                    local_symbol = req_info['exchange'] if not req_info['local_symbol'] == '' else req_info['symbol'])
                data['m_symbol'] = req_info['symbol']
                data['currency'] = req_info['currency']
        else:
            logging.info("未知的field：" +field)


    def tickSize(self, tickerId, field, size):
        """
        推送价格（量相关）
        """
        if field in tick_field:
            # 将合约信息取出
            req_info = self.req_dict[tickerId]
            sec_id = "ib.{exchange}.{local_symbol}".format(exchange = req_info['exchange'],
                                                        local_symbol = req_info['local_symbol'] if not req_info['local_symbol'] == '' else req_info['symbol'])
            # 取出映射的数据类型
            tick_key = tick_field[field]
            # 取出缓存中保存的数据
            data = self.tick_data[tickerId]
            if 'bid_volume' and 'bid_price' and 'ask_price' and 'ask_volume' \
                    and 'last_price' and 'last_volume' in data:
                data[tick_key] = size #更新数据
                utc_time = datetime.datetime.now()
                data['utc_time'] = utc_time
                copy_data = copy.deepcopy(data) #拍摄快照
                # 存入数据

                if 'volume' and 'high_price' and 'low_price' and 'pre_close_price' in data:
                    tick_collection = self.mongo_db[sec_id]
                    tick_collection.insert(copy_data)
                data['last_volume'] = 0
                logging.info("成功获取数据："+sec_id)
            else:
                # 将合约信息取出
                req_info = self.req_dict[tickerId]
                data[tick_key] = size
                # 将合约信息写入
                data['exchange'] = req_info['exchange']
                data['sec_id'] = "{exchange}.{local_symbol}".format(exchange = req_info['exchange'],
                                                                    local_symbol = req_info['local_symbol'] if not req_info['local_symbol'] == '' else req_info['symbol'])
                data['m_symbol'] = req_info['symbol']
                data['currency'] = req_info['currency']
        else:
            logging.error("未知的field:" + field)



    def tickOptionComputation(self, tickerId, field, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice):
        pass
    def tickGeneric(self, tickerId, tickType, value):
        pass
    def tickString(self, tickerId, tickType, value):
        pass
    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry):
        pass
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeId):
        pass
    def openOrder(self, orderId, contract, order, state):
        pass
    def openOrderEnd(self):
        pass
    def updateAccountValue(self, key, value, currency, accountName):
        pass
    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        pass
    def updateAccountTime(self, timeStamp):
        pass
    def accountDownloadEnd(self, accountName):
        pass
    def nextValidId(self, orderId):
        pass
    def contractDetails(self, reqId, contractDetails):
        pass
    def contractDetailsEnd(self, reqId):
        pass
    def bondContractDetails(self, reqId, contractDetails):
        pass
    def execDetails(self, reqId, contract, execution):
        pass
    def execDetailsEnd(self, reqId):
        pass
    def connectionClosed(self):
        pass
    def error(self, id=None, errorCode=None, errorMsg=None):
        print(errorCode,errorMsg)

    def error_0(self, strvalue=None):
        print(errorCode,errorMsg)

    def error_1(self, id=None, errorCode=None, errorMsg=None):
        print(error,errorMsg)

    def updateMktDepth(self, tickerId, position, operation, side, price, size):
        pass
    def updateMktDepthL2(self, tickerId, position, marketMaker, operation, side, price, size):
        pass
    def updateNewsBulletin(self, msgId, msgType, message, origExchange):
        pass
    def managedAccounts(self, accountsList):
        pass
    def receiveFA(self, faDataType, xml):
        pass
    def historicalData(self, reqId, date, open, high, low, close, volume, count, WAP, hasGaps):
        pass
    def scannerParameters(self, xml):
        pass
    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        pass
    def accountDownloadEnd(self, accountName):
        pass
    def commissionReport(self, commissionReport):
        pass
    def contractDetailsEnd(self, reqId):
        pass
    def currentTime(self, time):
        pass
    def deltaNeutralValidation(self, reqId, underComp):
        pass
    def execDetailsEnd(self, reqId):
        pass
    def fundamentalData(self, reqId, data):
        pass
    def marketDataType(self, reqId, marketDataType):
        pass
    def openOrderEnd(self):
        pass
    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        pass
    def scannerDataEnd(self, reqId):
        pass
    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry):
        pass
    def tickGeneric(self, tickerId, tickType, value):
        pass
    def tickSnapshotEnd(self, reqId):
        pass
    def error_0(self, strval):
        pass
    def error_1(self, id, errorCode, errorMsg):
        pass
    def position(self, account, contract, pos, avgCost):
        pass
    def positionEnd(self):
        pass
    def accountSummary(self, reqId, account, tag, value, currency):
        pass
    def accountSummaryEnd(self, reqId):
        pass


