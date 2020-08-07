# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/07

from flask import Blueprint

subscribe = Blueprint('subscribe', __name__)

from . import views, errors
