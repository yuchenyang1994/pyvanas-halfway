# -*- coding: utf-8 -*-
import datetime
import json
import logging

class CtpTask(object):

    """Ctp任务"""

    def __init__(self,redis_cli,mongo_db):
        """TODO: to be defined1.

        :redis_cli: TODO
        :mongo_db: TODO

        """
        self._redis_cli = redis_cli
        self._mongo_db = mongo_db
        self.time_cache = {}

    def bar_task_time(self,sec_id,rate, **kwargs):
        """任务"""
        tick = self._mongo_db[sec_id]
        # 如果制订了开始时间段
        if kwargs:
            utc_time_start = self.time_cache[sec_id] if sec_id in self.time_cache else kwargs[rate]
            utc_time_end = utc_time_start + datetime.timedelta(seconds=rate*60) # 计算出下一个时间
            flag = self._cal_bars(tick,sec_id,rate,utc_time_start,utc_time_end,False)
            self.time_cache[sec_id] = utc_time_end if flag else utc_time_start
        else:
            bar_tick_first = tick.find_one()
            utc_time_start = self.time_cache[sec_id] if sec_id in self.time_cache else bar_tick_first['utc_time']
            utc_time_start = datetime.datetime(utc_time_start.year,utc_time_start.month,utc_time_start.day,utc_time_start.hour,utc_time_start.minute)
            utc_time_end = utc_time_start + datetime.timedelta(seconds=rate*60)
            flag = self._cal_bars(tick,sec_id,rate,utc_time_start,utc_time_end,False)
            self.time_cache[sec_id] = utc_time_end if flag else utc_time_start

    def bar_task_day(self,sec_id,rate,**kwargs):
        """日线任务"""
        tick = self._mongo_db[sec_id]
        if kwargs:
            utc_time_start = self.time_cache[sec_id] if sec_id in self.time_cache else kwargs[rate]
            utc_time_end = utc_time_start + datetime.timedelta(days=rate) # 计算出下一个时间
            # 将下次的时间缓存起来
            flag = self._cal_bars(tick,sec_id,rate,utc_time_start,utc_time_end,True)
            self.time_cache[sec_id] = utc_time_end if flag else utc_time_start
        else:
            bar_tick_first = tick.find_one()
            if bar_tick_first:
                utc_time_start = self.time_cache[sec_id] if sec_id in self.time_cache else bar_tick_first['utc_time']
                utc_time_end = utc_time_start.date() + datetime.timedelta(days=rate*60)
                flag = self._cal_bars(tick,sec_id,rate,utc_time_start,utc_time_end,True)
                self.time_cache[sec_id] = utc_time_end if flag else utc_time_start
            else:
                pass

    def _cal_bars(self, tick_collection,sec_id,rate,start_time,end_time,is_dayliy):
        """docstring for _cal_bars"""
        time_cursor = tick_collection.find({
            'utc_time':{'$gte':start_time,'$lt':end_time}
        },
        {
            '_id':0
        }).sort('utc_time')
        # 转换为tick
        time_dict = [tick for tick in time_cursor]
        if len(time_dict)>1:
            high_prices = []
            low_prices = []
            bar_tick = {}
            for index,tick in enumerate(time_dict):
                # 区间开始
                if index == 0:
                    bar_tick['open'] = tick['open_price']
                    bar_tick['start_utc_time'] = tick['utc_time']
                    bar_tick['exchange'] = tick['exchange']
                    bar_tick['symbol'] = tick['symbol']
                    bar_tick['m_symbol'] = tick['m_symbol']

                elif index == len(time_dict)-1:
                    print(tick)
                    bar_tick['close'] = tick['last_price']
                    bar_tick['end_utc_time'] = tick['utc_time']
                    bar_tick['volume'] = tick['volume']
                    bar_tick['pre_close_price'] = tick['pre_close_price']
                    bar_tick['open_Interest'] = tick['open_Interest']

                high_prices.append(tick['high_price'])
                low_prices.append(tick['low_price'])
            bar_tick['count'] = len(time_dict)
            bar_tick['high_price'] = max(high_prices)
            bar_tick['low_price'] = min(low_prices)

            # 存库
            self._save_mongo(bar_tick,rate,is_dayliy)
            # 连续合约维护相关
            self._save_con(bar_tick)

            # 发布操作
            self._publis_data(bar_tick,rate,is_dayliy)
            return True
        else:
            return False

    def _save_mongo(self, bar_tick,rate,is_dayliy):
        """docstring for _save_mongo"""
        channel_name = "{sec_id}_{rate}_bar".format(sec_id=bar_tick['symbol'],rate=rate) if not is_dayliy else  "{sec_id}_{rate}days".format(sec_id=bar_tick['symbol'],rate=rate)
        db_name = 'ctp.{channel_name}'.format(channel_name=channel_name)
        self._mongo_db[db_name].insert(bar_tick)

    def _save_con(self,bar_tick):
        """docstring for _save_con"""
        symbol_mapping = self._mongo_db['ctp_symbol_mapping']
        mapping = symbol_mapping.find_one()
        try:
            if mapping[bar_tick['m_symbol']] == bar_tick['symbol']:
                symbol_con = 'ctp_{m_symbol}00'.format(m_symbol = bar_tick['m_symbol'])
                self._mongo_db[symbol_con].insert(bar_tick)
        except KeyError as e:
            logging.info('暂时不存在这个连续合约')
    def _publis_data(self, bar_tick,rate,is_dayliy):
        """docstring for _publis_data"""
        if not is_dayliy and rate == 1:
            str_start_utc_time = str(bar_tick['start_utc_time'])
            str_end_utc_time = str(bar_tick['end_utc_time'])
            bar_tick['start_utc_time'] = str_start_utc_time
            bar_tick['end_utc_time'] = str_end_utc_time
            channel_name = 'ctp_{symbol}_{rate}bar'.format(symbol = bar_tick['symbol'],rate=rate)
            del bar_tick['_id']
            self._redis_cli.publish(channel_name,json.dumps(bar_tick))



