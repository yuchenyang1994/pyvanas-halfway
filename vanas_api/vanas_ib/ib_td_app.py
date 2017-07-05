# -*- coding: utf-8 -*-

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.ext.EWrapper import EWrapper
from ib.ext.EClientSocket import EClientSocket
from tick_type import tick_field
import datetime
import copy




class IbApp(object):
    """IB链接器"""

    def __init__(self,host,port,client_id,req_dict,order_dict,tick_dict):
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
        self.warpper = IbTestWrapper(req_dict,order_dict,tick_dict)
        self.connection = EClientSocket(self.warpper)
        self.req_id = 0
        self.order_id = 0
        self.req_dict = req_dict
        self.order_dict = order_dict
        self.tick_dict = tick_dict

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
        self.tick_dict[self.req_id] = {} # 初始化Tick的数据

        #cache_symbol
        cache_symbol = m_local_symbol if ' ' not in m_local_symbol else m_local_symbol.replace(' ','_')

        # 将订阅合约信息保存在字典中
        self.req_dict[self.req_id]={'symbol':m_symbol,'currency':currency,'sec_type':m_sec_type,
                               'exchange':m_exchange,'local_symbol':cache_symbol}

    def send_order(self,order_dict):
        """发单"""
        # 发单ID
        self.order_id += 1
        contract = self._make_opt_contract(order_dict)
        order = self._make_opt_order(self.order_id,self.client_id,order_dict)
        self.connection.placeOrder(self.order_id,contract,order)
        self.connection.reqIds()
        self.order_dict[self.order_id] = order_dict
        return self.order_id

    def cancle_order(self, order_id):
        """撤单"""
        self.connection.cancelOrder(order_id)


    def run(self):
        """运行"""
        while True:
            pass

    def _make_opt_contract(self,order_dict):
        """docstring for make_opt_contract"""
        contract = Contract()
        contract.m_localSymbol = order_dict['m_local_symbol']
        contract.m_secType = order_dict['m_sec_type']
        contract.m_right = order_dict['m_right']
        contract.m_expiry = order_dict['m_expiry']
        contract.m_strike = order_dict['m_strike']
        contract.m_exchange = order_dict['m_exchange']
        contract.m_currency = order_dict['currency']
        return contract

    def _make_opt_order(self,order_id,client_id,order_dict):
        """docstring for _make_opt_contract"""
        order = Order()
        order.m_orderId = order_id
        order.m_clientId = client_id
        order.m_action = order_dict['m_action']
        order.m_lmtPrice = order_dict['price']
        order.m_totalQuantity = order_dict['volume']
        order.m_orderType = order_dict['m_order_type']
        return order


class IbTestWrapper(EWrapper):

    """
    Ib回调函数
    """

    def __init__(self,req_dict,order_dict,tick_data):
        """
        :req_dict:保存请求数据的字典
        """
        super(IbTestWrapper,self).__init__()
        self.req_dict = req_dict
        self.order_dict = order_dict


    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """
        :推送数据(价格相关
        """
        data = self._copy_tick(tickerId,field,price)

    def tickSize(self, tickerId, field, size):
        """
        推送价格（量相关）
        """
        data = self._copy_tick(tickerId,field,size)


    def tickOptionComputation(self, tickerId, field, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice):
        pass
    def tickGeneric(self, tickerId, tickType, value):
        pass
    def tickString(self, tickerId, tickType, value):
        pass
    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry):
        pass
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeId):
        if orderId in self.order_dict:
            # 将订单参数从缓存中取出
            order_all = self.order_dict[orderId]
            return_status = copy.deepcopy(order_all)
            return_status['status'] = status
            return_status['filled'] = filled
        else:
            print(orderId)
            od = {}
            od['order_id'] = orderId
            self.order_dict[orderId] = od
    def openOrder(self, orderId, contract, order, state):
        if orderId in self.order_dict:
            order_all = self.order_dict[orderId]
            return_od = copy.deepcopy(order_all)
            return_od['status'] = status
            return_od['direction'] = order.m_action
            return_od['price'] = order.m_lmtPrice
            return_od['total_volume'] = oder.m_totalQuantity
        else:
            od = {}
            od['order_id'] = orderId
            od['symbol'] = contract.m_localSymbol
            od['exchange'] = contract.m_exchange
            self.order_dict[orderId] = od


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
        trade = {}
        trade['getway'] = 'IB'
        trade['trade_id'] = execution.m_execId
        trade['symbol'] = contract.m_localSymbol
        trade['order_id'] = execution.m_orderId
        trade['price'] = execution.m_price
        trade['volume'] = execution.m_shares
        trade['tradeTime'] = execution.m_time
    def execDetailsEnd(self, reqId):
        pass
    def connectionClosed(self):
        msg = {'msg':"IB接口已经关闭"}
    def error(self, id=None, errorCode=None, errorMsg=None):
        error = {}
        error['error_id'] = errorCode
        error['error_msg'] = errorMsg

    def error_0(self, strvalue=None):
        error = {}
        error['error_msg'] = strvalue

    def error_1(self, id=None, errorCode=None, errorMsg=None):
        error = {}
        error['error_id'] = errorCode
        error['error_msg'] = errorMsg


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
        print(time)
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
    def _copy_tick(self,tickerID,field,price):
        """docstring for copy_tick"""
        if field in tick_field:
            # 将合约信息取出
            req_info = self.req_dict[tickerID]
            # 取出映射的数据类型
            tick_key = tick_field[field]
            # 取出缓存中保存的数据
            data = self.tick_data[tickerID]
            # 如果买卖最后尺寸和价格存在，那么拍摄快照
            if 'bid_volume' and 'bid_price' and 'ask_price' and 'ask_volume' \
                    and 'last_price' and 'last_volume' in data:
                data[tick_key] = price
                utc_time = datetime.datetime.now()
                data['utc_time'] = utc_time
                copy_data = copy.deepcopy(data)
                if 'high_price' and 'low_price' and 'volume' and 'pre_close_price' in data:
                    return copy_data
                    # 否则等数据写入后再说
            else:
                #将合约信息取出
                req_info = self.req_dict[tickerID]
                data[tick_key] = price
                #将合约信息写入
                data['exchange'] = req_info['exchange']
                data['sec_id'] = "{exchange}.{local_symbol}".format(exchange = req_info['exchange'],
                                                                    local_symbol = req_info['local_symbol'])
                data['currency'] = req_info['currency']
        else:
            print(field)


if __name__ == "__main__":
    req_dict = {}
    tick_dict = {}
    r = redis.StrictRedis(host = '127.0.0.1',port=6379,db=0)
    mongo_cli = MongoClient('139.196.6.151',port=26666)
    pyvanas_db = mongo_cli['pyvanas_test']
    app = IbApp('139.196.185.91',7496,14,req_dict,tick_dict,r,pyvanas_db)
    app.econnect()
    app.subscribe("NIKKEI225M","JPY","FUT","OSE.JPN","161120019")
    app.run()



