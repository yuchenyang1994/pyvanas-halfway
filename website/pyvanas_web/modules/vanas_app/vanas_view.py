# -*- coding: utf-8 -*-

from flask import Blueprint


vanas = Blueprint('vanas',__name__,template_folder='templates')

@vanas.route('/')
def index():
    """主页
    """
    return 'Hello,Vanas!'
