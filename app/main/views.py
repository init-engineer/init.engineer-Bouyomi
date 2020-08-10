# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/05

from flask import render_template, Response
from . import main
from ..utils import chart, makedirs, sseserver


@main.route('/')
def index():
    makedirs.MakeDirs()
    chart.Chart()
    return render_template('index.html')


@main.route('/subscribe')
def subscribe():
    publish = sseserver.SseServer()
    return Response(publish.getInstance().subscribe(), content_type='text/event-stream')
