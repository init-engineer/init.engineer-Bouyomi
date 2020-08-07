# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/07


import time
import json


from sse import Publisher


publisher = Publisher()


def publish(channel, author, message):
    publisher.publish(
    json.dumps({
        "channel": channel,
        "author": author,
        "message": message,
        "time": time.strftime("%H:%M:%S")
    }))


if __name__ == '__main__':
    pass
