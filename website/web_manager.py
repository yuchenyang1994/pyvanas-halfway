# -*- coding: utf-8 -*-

from pyvanas_web.app import create_app
from flask_script import Manager
from pyvanas_web.extensions import socketio

app = create_app()
manager = Manager(app)

@manager.command
def run():
    socketio.run(app,host='0.0.0.0',port=2000)

if __name__ == "__main__":
    manager.run()
