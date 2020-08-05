# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/05

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
