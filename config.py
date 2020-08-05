# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/05

import os
import json

from collections import namedtuple


basedir = os.path.abspath(os.path.dirname(__file__))


def get(file):
    try:
        with open(file, encoding='utf-8') as data:
            return json.load(data, object_hook = lambda d: namedtuple('X', d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("命令執行失敗。")
    except FileNotFoundError:
        raise FileNotFoundError("找不到 JSON 檔案。")


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'xxx'

    CACHE_KEY = "bouyomi:%s"

    @staticmethod
    def init_app(app):
        pass


# 開發
class DevelopmentConfig(Config):
    DEBUG = True


# 測試
class TestingConfig(Config):
    TESTING = True


# 正式
class ProductionConfig(Config):
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}