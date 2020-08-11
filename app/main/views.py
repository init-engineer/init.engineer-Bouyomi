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
    return render_template('socket_index.html')
    # return render_template('sse_index.html')


@main.route('/subscribe')
def subscribe():
    # SSE Server
    publish = sseserver
    publish = publish.SseServer()
    return Response(publish.instance.subscribe(), content_type='text/event-stream')
