# -*- coding: utf-8 -*-
import logging
import os
from config import BaseConfig




def create_file_logger(log_file, loger_level):
    log_file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=100000, backupCount=10)
    log_file_handler.setLevel(loger_level)
    log_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s ')
    )
    return log_file_handler


# 配置 APP Log
def configure_app_logger(app):
    logger_level = app.config['LOG_LEVEL']

    # App Logger
    app.logger.addHandler(
        create_file_logger(os.path.join(BaseConfig.LOG_FOLDER, BaseConfig.LOG_FILE), logger_level))

    # Console Logger

    # Skip debug and test mode. Just check standard output.
    if app.debug or app.testing:
        pass

    # Logger
    app.logger.info("App Logger: %r" % logger_level)
    app.logger.info("  MDB Name: %r" % app.config['MONGODB_DB'])



#
# 配置默认日志信息
#
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filemode='w')

# 定义一个Handler打印INFO及以上级别的日志到sys.stderr
#console = logging.StreamHandler()
#console.setLevel(BaseConfig.LOG_LEVEL)
#console.setFormatter(logging.Formatter('%(asctime)-12s: %(levelname)-8s %(message)s'))  # 设置日志打印格式
#
## 将定义好的console日志handler添加到root logger
#logger = logging.getLogger('')
#logger.addHandler(console)
