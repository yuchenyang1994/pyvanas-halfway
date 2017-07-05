# coding:utf-8
from gmsdk import md,to_dict
import time
import datetime
import pymongo



# 读取期货列表
f_list = list()
with open('list.txt','r') as f:
    lines = f.readlines()
    for line in lines:
        i = line.split(' ')
        f_list.append(i[0])

# 初始化行情服务器
ret = md.init('13063638616','940304',mode =1)
print ret
##########################
'''
设置数据库
'''
conn = pymongo.MongoClient('139.196.6.151',26666)
db = conn['test_center']
qh_data_one_min = db['qh_data_one_min']
qh_data_five_min = db['qh_data_five_min']
qh_data_five_daily = db['qh_data_five_daily']
###############################
end = datetime.datetime.now()
start_m = end.month - 1
start = datetime.datetime(end.year,start_m,1,9,0,0)
start_e = datetime.datetime(end.year,start_m,1,15,0,0)
e_s_timedetlta = (end - start).days
for day in range(e_s_timedetlta):
    this_start = start + datetime.timedelta(days=day)
    this_end = start_e + datetime.timedelta(days=day)
    for f in f_list:
        bars = md.get_bars(f, 60, this_start.strftime('%Y-%m-%d %H:%M:%S'),this_end.strftime('%Y-%m-%d %H:%M:%S'))
        for bar in bars:
            print to_dict(bar)
            qh_data_one_min.insert_one(to_dict(bar))
    time.sleep(2)

for day in range(e_s_timedetlta):
    this_start = start + datetime.timedelta(days=day)
    this_end = start_e + datetime.timedelta(days=day)
    for f in f_list:
        bars = md.get_bars(f, 300, this_start.strftime('%Y-%m-%d %H:%M:%S'),this_end.strftime('%Y-%m-%d %H:%M:%S'))
        for bar in bars:
            print to_dict(bar)
            qh_data_five_min.insert(to_dict(bar))
    time.sleep(2)

for day in range(e_s_timedetlta):
    daily_start = start.date() + datetime.timedelta(days=day)
    daily_end = start_e.date() + datetime.timedelta(days=day)
    for f in f_list:
        bars = md.get_bars(f, 300, daily_start.strftime('%Y-%m-%d %H:%M:%S'),daily_end.strftime('%Y-%m-%d %H:%M:%S'))
        for bar in bars:
            print to_dict(bar)
            qh_data_five_daily.insert(to_dict(bar))
    time.sleep(2)