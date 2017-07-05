# -*- coding: utf-8 -*-
import datetime
import json
import logging

class IbTask(object):
    """IB任务"""
    def __init__(self,redis_cli,mongo_db):
        """

        :redis: redis服务器
        :mongo_db: mongo_db服务

        """
        self._redis = redis_cli
        self._mongo_db = mongo_db
        self.time_cache = {}

    def bar_task_time(self,sec_id,rate,**kwargs):
        """任务"""
        tick = self._mongo_db[sec_id]
        # 如果指定了了开始时间段
        if kwargs:
            utc_time_start = self.time_cache[sec_id] if sec_id in self.time_cache else kwargs[rate]
            utc_time_end = utc_time_start + datetime.timedelta(seconds=rate*60) #计算出下一个时间
            flag = self._cal_bars(tick,sec_id,rate,utc_time_start,utc_time_end,False)
            #将下次时间缓存起来
            self.time_cache[sec_id] = utc_time_end if flag else utc_time_start

        else:
            bar_tick_first = tick.find_one()
            if bar_tick_first:
                utc_time_start = self.time_cache[sec_id] if sec_id in self.time_cache else bar_tick_first['utc_time'] # 如果已经有了缓存用缓存中下一个时间，如果没有那么用第一条时间
                utc_time_start = datetime.datetime(utc_time_start.year,utc_time_start.month,utc_time_start.day,utc_time_start.hour,utc_time_start.minute)
                utc_time_end = utc_time_start + datetime.timedelta(seconds = rate * 60) # 计算下一个时间
                flag = self._cal_bars(tick,sec_id,rate,utc_time_start,utc_time_end,False) # 处理bar时间
                self.time_cache[sec_id] = utc_time_end if flag else utc_time_start
            else:
                pass
    def bar_task_day(self,sec_id,rate, **kwargs):
        """docstring for bar_task_time"""
        tick = self._mongo_db[sec_id]
        # 如果指定了了开始时间段
        if kwargs:
            utc_time_start = self.time_cache[sec_id] if sec_id in self.time_cache else kwargs[rate]
            utc_time_end = utc_time_start.date() + datetime.timedelta(days=1) #计算出下一个时间
            flag = self._cal_bars(tick,sec_id,rate,utc_time_start,utc_time_end,True)
            self.time_cache[sec_id] = utc_time_end if flag else utc_time_start
            #将下次时间缓存起来

        else:
            bar_tick_first = tick.find_one()
            utc_time_start = self.time_cache[sec_id] if sec_id in self.time_cache else bar_tick_first['utc_time'] # 如果已经有了缓存用缓存中下一个时间，如果没有那么用第一条时间
            utc_time_end = utc_time_start.date() + datetime.timedelta(days=1) # 计算下一个时间
            flag = self._cal_bars(tick,sec_id,rate,utc_time_start,utc_time_end) # 处理bar时间
            self.time_cache[sec_id] = utc_time_end if flag else utc_time_start



    def _cal_bars(self,tick_collection,sec_id,rate, start_time,end_time,is_dayliy):
        """计算bar的函数"""
        time_cursor = tick_collection.find({
                    'utc_time':{'$gte':start_time,'$lt':end_time}
                },
                {
                    '_id':0
                }).sort('utc_time')

        # 转换为tick
        time_dict = [ticks for ticks in time_cursor]
        if len(time_dict)>1:
            high_prices= []
            low_prices = []
            bar_tick={} # 区间内容
            for index,tick in enumerate(time_dict):
                # 区间开始
                if index == 0:
                    if tick['exchange'] == 'IDEALPRO':
                        bar_tick['open'] = (tick['bid_price'] + tick['ask_price'])/2
                    else:
                        bar_tick['open'] = tick['last_price'] # 开盘价
                    bar_tick['start_utc_time'] = tick['utc_time'] # 区间开始时间
                    bar_tick['exchange'] = tick['exchange'] # 交易所
                    bar_tick['sec_id'] = tick['sec_id'] # 合约ID
                    bar_tick['m_symbol'] = tick['m_symbol']
                    bar_tick['currency'] = tick['currency'] # 币种


                # 区间的结束
                elif index == len(time_dict)-1:
                    if tick['exchange'] == 'IDEALPRO':
                        bar_tick['close'] = (tick['bid_price'] + tick['ask_price'])/2 # 区间截至收盘价
                        bar_tick['volume'] = 0
                    else:
                        bar_tick['close'] = tick['last_price'] # 区间截至收盘价
                        bar_tick['volume'] = tick['volume']
                    bar_tick['end_utc_time'] = tick['utc_time'] # 区间截至时间
                    self.time_cache[bar_tick['sec_id']] = tick['utc_time']

                # 计算最高/最低买卖价和累计成交量
                high_prices.append(tick['high_price']) # 将所有最高价放入列表
                low_prices.append(tick['low_price']) # 将所有最低价放入列表
            bar_tick['count'] = len(time_dict) # 区间截至次数
            bar_tick['high_price'] = max(high_prices) # 区间最高价
            bar_tick['low_price'] = min(low_prices) # 区间最低价
            # 存库操作
            self._save_mongo(bar_tick,rate,is_dayliy)
            # 维护连续合约相关
            self._save_con(bar_tick)
            # 发布操作
            self._publis_data(bar_tick,rate,is_dayliy)
            return True
        else:
            return False

    def _save_mongo(self, bar_tick,rate,is_dayliy):
        """docstring for fname"""
        channel_name = "{sec_id}_{rate}_bar".format(sec_id=bar_tick['sec_id'],rate=rate) if not is_dayliy else "{sec_id}_{rate}days_bar".format(sec_id=bar_tick['sec_id'],rate=rate)
        db_name = 'ib.{channel_name}'.format(channel_name=channel_name)
        self._mongo_db[db_name].insert(bar_tick)

    def _save_con(self,bar_tick):
        """docstring for _save_con"""
        symbol_mapping = self._mongo_db['ib_symbol_mapping'] # 获取映射配置
        mapping = symbol_mapping.find_one() # 将映射配置读取出来
        symbol = bar_tick['sec_id'].split('.') # 将合约ID切片
        try:
            exchange_symbol = mapping[bar_tick['exchange']]
            if exchange_symbol[bar_tick['m_symbol']]  == symbol[1]:
                symbol_con = 'ib_{m_symbol}00'.format(m_symbol = bar_tick['m_symbol'])
                self._mongo_db[symbol_con].insert(bar_tick)
        except KeyError:
            logging.info('暂时不存在这个连续合约,请去界面中设置')

    def _publis_data(self, bar_tick,rate,is_dayliy):
        """docstring for _publis_data"""
        if not is_dayliy and rate == 1:
            str_start_utc_time = str(bar_tick['start_utc_time'])
            str_end_utc_time = str(bar_tick['end_utc_time'])
            bar_tick['start_utc_time'] = str_start_utc_time
            bar_tick['end_utc_time'] = str_end_utc_time
            channel_name = 'ib_{sec_id}_{rate}bar'.format(sec_id=bar_tick['sec_id'],rate=rate)
            del bar_tick['_id']
            self._redis.publish(channel_name,json.dumps(bar_tick))










