# -*- coding: utf-8 -*-

from ib.ext.Contract import Contract
from ib.ext.EWrapper import EWrapper
from ib.ext.EClientSocket import EClientSocket
import datetime

def showmessage(message, mapping):
    """TODO: Docstring for showmessage.

    :message: TODO
    :mapping: TODO
    :returns: TODO

    """
    try:
        del(mapping['self'])
    except (KeyError, ):
        pass
    items = list(mapping.items())
    items.sort()
    print(('### %s time: %s' % (message,datetime.datetime.now() )))
    for k, v in items:
        print(('    %s:%s' % (k, v)))

class IbTextApp(object):

    """IB链接器"""

    def __init__(self,host,port,client_id):
        """
        TODO: 不应该维护一个巨大的类，可以考虑使用混合模式来管理这个类
        :host:地址
        :port:接口
        :client_id:这个可以随便写一个,int
        :req_id:请求id
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.warpper = IbTestWrapper()
        self.connection = EClientSocket(self.warpper)
        self.req_id = 0

    def econnect(self):
        """docstring for connect"""
        self.connection.eConnect(self.host,self.port,self.client_id)

    def subscribe(self):
        """
        :return: 返回req_id和合约代码信息返回,好做好映射，
        """
        contract = Contract()
        contract.m_symbol = "EUR" # 底层资产的代码 PS:CL
        contract.m_currency = "USD" # 币种 PS:USD
        contract.m_secType = "CASH" # 证券类型 PS:FUT
        contract.m_exchange = "IDEALPRO" # 交易所NYMEX
        contract.m_localSymbol = "" #合约代码
        self.connection.reqMktData(self.req_id+1,contract,'',False)
    def query_account(self,acc_code):
        """
        docstring for query_account
        查询账户信息
        似乎是主动推送
        """
        self.connection.reqAccountUpdates(1, acc_code)
    def req_history_data(self):
        contract = Contract()
        contract.m_symbol = 'CL'
        contract.m_secType = 'FUT'
        contract.m_exchange = 'NYMEX'
        contract.m_localSymbol = "CLX6"
        endtime = '20161014 15:30:30'
        self.connection.reqHistoricalData(
            tickerId = 1,
            contract = contract,
            endDateTime=endtime,
            durationStr = '1 D',
            barSizeSetting='1 min',
            whatToShow =  'TRADES',
            useRTH=0,
            formatDate=1
        )



class IbTestWrapper(EWrapper):

    """Docstring for IbTestWrapper. """

    def __init__(self):
        """
        :req_dict:请求ID和名称的集合
        """
        super(IbTestWrapper,self).__init__()
    def tickPrice(self, tickerId, field, price, canAutoExecute):
        print("I tick")
        showmessage('tickPrice', vars())

    def tickSize(self, tickerId, field, size):
        showmessage('tickSize', vars())

    def tickOptionComputation(self, tickerId, field, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice):
        showmessage('tickOptionComputation', vars())

    def tickGeneric(self, tickerId, tickType, value):
        showmessage('tickGeneric', vars())

    def tickString(self, tickerId, tickType, value):
        showmessage('tickString', vars())

    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry):
        showmessage('tickEFP', vars())

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeId):
        showmessage('orderStatus', vars())

    def openOrder(self, orderId, contract, order, state):
        showmessage('openOrder', vars())

    def openOrderEnd(self):
        showmessage('openOrderEnd', vars())

    def updateAccountValue(self, key, value, currency, accountName):
        showmessage('updateAccountValue', vars())

    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        showmessage('updatePortfolio', vars())

    def updateAccountTime(self, timeStamp):
        showmessage('updateAccountTime', vars())

    def accountDownloadEnd(self, accountName):
        showmessage('accountDownloadEnd', vars())

    def nextValidId(self, orderId):
        showmessage('nextValidId', vars())

    def contractDetails(self, reqId, contractDetails):
        showmessage('contractDetails', vars())

    def contractDetailsEnd(self, reqId):
        showmessage('contractDetailsEnd', vars())

    def bondContractDetails(self, reqId, contractDetails):
        showmessage('bondContractDetails', vars())

    def execDetails(self, reqId, contract, execution):
        showmessage('execDetails', vars())

    def execDetailsEnd(self, reqId):
        showmessage('execDetailsEnd', vars())

    def connectionClosed(self):
        showmessage('connectionClosed', {})

    def error(self, id=None, errorCode=None, errorMsg=None):
        showmessage('error', vars())

    def error_0(self, strvalue=None):
        showmessage('error_0', vars())

    def error_1(self, id=None, errorCode=None, errorMsg=None):
        showmessage('error_1', vars())

    def updateMktDepth(self, tickerId, position, operation, side, price, size):
        showmessage('updateMktDepth', vars())

    def updateMktDepthL2(self, tickerId, position, marketMaker, operation, side, price, size):
        showmessage('updateMktDepthL2', vars())

    def updateNewsBulletin(self, msgId, msgType, message, origExchange):
        showmessage('updateNewsBulletin', vars())

    def managedAccounts(self, accountsList):
        showmessage('managedAccounts', vars())

    def receiveFA(self, faDataType, xml):
        showmessage('receiveFA', vars())

    def historicalData(self, reqId, date, open, high, low, close, volume, count, WAP, hasGaps):
        showmessage('historicalData', vars())

    def scannerParameters(self, xml):
        showmessage('scannerParameters', vars())

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        showmessage('scannerData', vars())

    def accountDownloadEnd(self, accountName):
        showmessage('acountDownloadEnd', vars())

    def commissionReport(self, commissionReport):
        showmessage('commissionReport', vars())

    def contractDetailsEnd(self, reqId):
        showmessage('contractDetailsEnd', vars())

    def currentTime(self, time):
        showmessage('currentTime', vars())

    def deltaNeutralValidation(self, reqId, underComp):
        showmessage('deltaNeutralValidation', vars())

    def execDetailsEnd(self, reqId):
        showmessage('execDetailsEnd', vars())

    def fundamentalData(self, reqId, data):
        showmessage('fundamentalData', vars())

    def marketDataType(self, reqId, marketDataType):
        showmessage('marketDataType', vars())

    def openOrderEnd(self):
        showmessage('openOrderEnd', vars())

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        showmessage('realtimeBar', vars())

    def scannerDataEnd(self, reqId):
        showmessage('scannerDataEnd', vars())

    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry):
        showmessage('tickEFP', vars())

    def tickGeneric(self, tickerId, tickType, value):
        showmessage('tickGeneric', vars())

    def tickSnapshotEnd(self, reqId):
        showmessage('tickSnapshotEnd', vars())

    def error_0(self, strval):
        showmessage('error_0', vars())

    def error_1(self, id, errorCode, errorMsg):
        showmessage('error_1', vars())

    def position(self, account, contract, pos, avgCost):
        showmessage('position', vars())

    def positionEnd(self):
        showmessage('positionEnd', vars())

    def accountSummary(self, reqId, account, tag, value, currency):
        showmessage('accountSummary', vars())

    def accountSummaryEnd(self, reqId):
        showmessage('accountSummaryEnd', vars())



if __name__ == "__main__":
    app = IbTextApp('139.196.185.91',7496,12)
    app.econnect()
    app.subscribe()
    while True:
        pass


