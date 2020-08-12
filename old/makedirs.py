# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/10

import os
import time


class MakeDirs(object):

    def __init__(self):
        print("[DEBUG] 檢查存放資料夾中 ...")

        _now_timestamp = int(time.time())
        _now_array = time.localtime(_now_timestamp)
        _now_day_string = time.strftime("%Y-%m-%d", _now_array)

        exists("./talks")
        exists("./talks/voices")
        exists("./talks/voices/" + _now_day_string)
        exists("./talks/xmls")
        exists("./talks/xmls/" + _now_day_string)
        pass


def exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("[DEBUG] " + path + " 資料夾不存在，執行新增動作。")
    else:
        print("[DEBUG] " + path + " 資料夾已存在。")
