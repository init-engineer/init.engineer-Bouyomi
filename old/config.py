# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/05

import os
import json

from collections import namedtuple


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'xxx'
    CACHE_KEY = "bouyomi:%s"


    # 微軟 Azure 文字轉語音服務
    # 
    SPEECH_ACTIVE = False
    SPEECH_TOKEN = "YOUR-SPEECH-TOKEN"
    SPEECH_REGION = "YOUR-SPEECH-REGION"
    SPEECH_VOICE_NAME = "YOUR-SPEECH-VOICE-NAME"
    SPEECH_VOICE_PROSODY_RATE = 1.0


    # Twitch 直播留言設定
    # [!注意!]
    #   至少需要 TWITCH_CHANNEL、TWITCH_OAUTH_TOKEN 這兩項資料，才能啟動聊天室監聽服務
    #   OAuth Token 可以從這裡獲得 https://twitchapps.com/tmi/
    TWITCH_ACTIVE = False
    TWITCH_CHANNEL = "YOUR_TWITCH_CHANNEL"
    TWITCH_NICKNAME = "YOUR_TWITCH_NICKNAME"
    TWITCH_OAUTH_TOKEN = "YOUR_TWITCH_OAUTH_TOKEN"
    TWITCH_CLIENT_ID = "YOUR_TWITCH_CLIENT_ID"
    TWITCH_BEARER_TOKEN = "YOUR_TWITCH_BEARER_TOKEN"


    # Facebook 直播留言設定
    # [!注意!]
    #   Access Token 必須擁有 publish_pages 的權限，以獲得公開的留言資訊。
    #   Live video id 是每次開啟直播後，直播所給予的 ID，所以每次直播都需要更新這項資料。
    FACEBOOK_ACTIVE = False
    FACEBOOK_ACCESS_TOKEN = "YOUR_FACEBOOK_ACCESS_TOKEN"
    FACEBOOK_LIVE_VIDEO_ID = "YOUR_FACEBOOK_LIVE_VIDEO_ID"


    # YouTube 直播留言設定
    # [!注意!]
    #   Live video id 是每次開啟直播後，直播所給予的 ID，所以每次直播都需要更新這項資料。
    YOUTUBE_ACTIVE = False
    YOUTUBE_LIVE_VIDEO_ID = "YOUR_YOUTUBE_VIDEO_ID"


    # DouYu 直播留言設定
    DOUYU_ACTIVE = False
    DOUYU_ROOM_ID = "YOUR_DOUYU_ROOM_ID"
    DOUYU_BARRAGE_HOST = "YOU_DOUYU_BARRAGE_HOST"


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