# coding:utf-8

from vanas_md.vnctpmd import MdApi
from colorama import Fore, Back, Style
from time import sleep
from pymongo import MongoClient


def print_dict(d):
    for key, value in d.items():
        print (Fore.RED + key + ':' + Fore.GREEN + str(value))


def simple_log(func):
    def wrapper(*args, **kw):
        print ""
        print str(func.__name__)
        return func(*args, **kw)
    return wrapper

########################################################################


class TestMdApi(MdApi):
    """测试用实例"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(TestMdApi, self).__init__()
        self.client = MongoClient('139.196.6.151', 26666)
        self.db = self.client['test_center']

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

    @simple_log
    def onRspSubMarketData(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(error)
        print_dict(data)
    #----------------------------------------------------------------------

    @simple_log
    def onRspUnSubMarketData(self, data, error, n, last):
        """退订合约回报"""
        print_dict(error)
        print_dict(data)
    #----------------------------------------------------------------------

    @simple_log
    def onRtnDepthMarketData(self, data):
        """行情推送"""
        print(data)

    #----------------------------------------------------------------------
    @simple_log
    def onRspSubForQuoteRsp(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(error)
        print_dict(data)
    #----------------------------------------------------------------------

    @simple_log
    def onRspUnSubForQuoteRsp(self, data, error, n, last):
        """退订合约回报"""
        print_dict(error)
        print_dict(data)

    #----------------------------------------------------------------------
    @simple_log
    def onRtnForQuoteRsp(self, data):
        """行情推送"""
        print_dict(data)

    def run(self):
        while True:
            sleep(0.5)

#----------------------------------------------------------------------


def start(userid, userpassword):
    """主测试函数，出现堵塞时可以考虑使用sleep"""
    reqid = 0

    # 创建Qt应用对象，用于事件循环

    # 创建API对象
    api = TestMdApi()

    # 在C++环境中创建MdApi对象，传入参数是希望用来保存.con文件的地址
    api.createFtdcMdApi('./vanas_con/')

    # 注册前置机地址
    api.registerFront("tcp://180.168.146.187:10011")

    # 初始化api，连接前置机
    api.init()
    sleep(0.5)

    # 登陆
    loginReq = {}                           # 创建一个空字典
    loginReq['UserID'] = userid                 # 参数作为字典键值的方式传入
    loginReq['Password'] = userpassword               # 键名和C++中的结构体成员名对应
    loginReq['BrokerID'] = '9999'
    reqid = reqid + 1                       # 请求数必须保持唯一性
    api.reqUserLogin(loginReq, reqid)
    sleep(0.5)

    # 登出，测试出错（无此功能）
    #reqid = reqid + 1
    #i = api.reqUserLogout({}, 1)
    # sleep(0.5)

    # 安全退出，测试通过
    # i = api.exit()

    # 获取交易日，目前输出为空
    day = api.getTradingDay()
    print 'Trading Day is:' + str(day)
    sleep(0.5)

    # 订阅合约，测试通过
    # api.subscribeMarketData('ru1701')
    # api.subscribeMarketData('rb1701')

    api.subscribeMarketData()
    # api.subscribeMarketData('cu1701')
    # api.subscribeMarketData('zn1701')

    # api.subscribeMarketData('cu1701')
    #
    # 退订合约，测试通过
    # i = api.unSubscribeMarketData('IF1701')
    # print i
    # 订阅询价，测试通过
    # 退订询价，测试通过
    # i = api.unSubscribeForQuoteRsp('IO1701-C-3900')
    # print i
    # 连续运行，用于输出行情
    while True:
        pass
if __name__ == '__main__':
    start('069586', '940304')
