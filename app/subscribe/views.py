# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/07

import flask

from . import subscribe
from sse import Publisher


publisher = Publisher()


@subscribe.route('/subscribe')
def index():
    return flask.Response(publisher.subscribe(), content_type='text/event-stream')
