自动化交易平台数据系统
================================

![pyvanas](http://i1.piimg.com/4851/ba6f5634e2eefec2.jpg)

目录结构
--------------------------------
TODO:....


环境相关
--------------------------------
### 安装boost库和boost-lib
* ubuntu
    1. `sudo apt-get install build-essential`
    2. `sudo apt-get install libboost-all-dev`
    3. `sudo apt-get install python-dev`
    4. `sudo apt-get install cmake`

* arch
    1. `yaourt boost`
    2. `yaourt boost-lib`
    3. `yaourt cmake`

* centos
    1. `sudo yum install boost`
    2. `sudo yum install boost-devel`
    3. `sudo yum install cmake`

* 进入vanas_api/vanas_build运行build.sh 完成编译

### IB相关

1. 进入vanas_api/IbPy-master/
2. `python setup.py install`
### 行情服务开启
* IB
    1. 开启行情实时获取推送服务 `python ib_md_service.py`
    2. 开启实时bar数据生成推送服务 `python ib_task_manager.py <分钟线>_bar <频率数 如：1>` ps:`python ib_task_manager.py 1_bar 1`
    3. 配置ib TWS服务 在conf/config.py 中修改
    4. 在vanas_task/ib_bar_jobs.py 中编写你想要频率的函数并且在bar_jobs中注册

* CTP
    1. 开启行情服务获取推送服务 `python ctp_md_service.py`
    2. 开启实时bar数据生成推送服务 `python ib_task_manager.py <分钟线>_bar <频率数 如：1>` ps : `python ib_task_manager.py 1_bar 1`
    3. 配置CTP接口的数据服务参数 在conf/config.py 中修改
    4. 在vanas_task/ctp_bar_jobs.py 中编写你想要的频率的函数并且在bar_jobs中注册

### Quick Start

`nohup python ib_md_service.py > log/ib.log &`
`nohup python ctp_md_service.py > log/ctp.log &`
`nohup python ib_task_manager.py 1_bar 1 > log/ib_1bar.log &`
`nohup python ctp_task_manager.py 1_bar 1 > log/ctp_1bar.log &`
`nohup python ib_task_manager.py 5_bar 5 > log/ib_5bar.log &`
`nohup python ctp_task_manager.py 5_bar 5 > log/ctp_5bar.log &`


Todo
-------------------------------


- [x] 数据接入
    - [x] 指定标准的数据模型
    - [x] CTP接口读取
    - [x] IB接口

- [ ] 数据维护
    - [x] 实时数据存储
    - [x] 实时bar数据
    - [x] 数据推送

- [ ] WEB管理界面
    - [ ] 历史数据可视化
    - [ ] 实时数据可视化
    - [ ] 增删订阅
    - [ ] 用户管理

- [ ] 策略系统
    - [ ] 将交易的主动接口封装调用
    - [x] 提供历史数据
    - [ ] 在web管理界面监控日志和可视化操作
