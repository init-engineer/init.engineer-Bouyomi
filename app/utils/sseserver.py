# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/07

import time
import json

from .sse import Publisher


class SseServer:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if SseServer.__instance is None:
            SseServer()
            print('SSE Server 不存在，重新呼叫 ...')
        print('回傳 SSE Server')
        return SseServer.__instance 

    def __init__(self):
        """ Virtually private constructor. """
        if self.__instance is None:
            self.__instance = Publisher()
            print('建立 SSE Server ...')
