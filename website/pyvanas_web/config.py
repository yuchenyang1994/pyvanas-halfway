# -*- coding: utf-8 -*-
import logging
import os

class BaseConfig(object):

    PROJECT = "pyvanas"

    # Get app root path, also can use flask.root_path.
    # ../../config.py
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Debug
    DEBUG = True
    TESTING = False


    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = '2SdFEgf87yn3$s*dfe34343gfghjhj$3'

    # Instance folder path, make it independent.
    INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance', PROJECT)

    # Logger
    LOG_LEVEL = logging.DEBUG
    LOG_FILE = 'output.log'
    LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')

    # redis
    REDIS_URL = "redis://localhost:6379/0"

    # MONGO
    MONGO_HOST = "139.196.6.151"
    MONGO_PORT = 26666
    MONGO_DBNAME = "pyvanas_test"




