# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/07

import time
import json

from .sse import Publisher


class SseServer:
    # Here will be the instance stored.
    instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if SseServer.instance is None:
            SseServer()
            print('SSE Server 不存在，重新呼叫 ...')
        print('回傳 SSE Server')
        return SseServer.instance 

    def __init__(self):
        """ Virtually private constructor. """
        if self.instance is None:
            self.instance = Publisher()
            print('建立 SSE Server ...')
