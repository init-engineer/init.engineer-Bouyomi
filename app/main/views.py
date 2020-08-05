# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/05

from flask import render_template, flash
from . import main

@main.route('/')
def index():
    return render_template('index.html')
