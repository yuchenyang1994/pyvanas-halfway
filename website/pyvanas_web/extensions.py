# -*- coding: utf-8 -*-
from flask.ext.pymongo import PyMongo
from flask.ext.redis import FlaskRedis
from flask_socketio import SocketIO

# mongodb
mongo = PyMongo()

# redis
redis_store = FlaskRedis()

# socketIO
socketio = SocketIO()
