# -*- coding: utf-8 -*-

from pyvanas_web.extensions import socketio
from flask_socketio import send,emit
import time

@socketio.on('conect',namespace='/ib')
def connect():
    """链接时
    :returns: TODO

    """
    emit('on_connect',{'data':'connected'})

@socketio.on('in',namespace='/ib')
def on_join(data):
    """进入room

    :data: TODO
    :returns: TODO

    """
    print(data)
