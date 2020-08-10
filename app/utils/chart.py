# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/07


import time
import json
import string
import twitch
import random
import sseclient
import threading

from . import voice, sseserver
from config import Config
from pytchat import CompatibleProcessor
from pytchat import LiveChat as youtubeClient
from pydouyu.client import Client as douyuClient


class Chart(object):
    _instance = None
    _threadFacebook = None
    _threadTwitch = None
    _threadYoutube = None
    _threadDouyu = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if Config.FACEBOOK_ACTIVE:
            if self._threadFacebook is None:
                print("啟動 Facebook 直播監聽 ...")
                self._threadFacebook = threading.Thread(target=facebookLiveChat)
                self._threadFacebook.start()
                pass
            else:
                print("Facebook 直播監聽正在運作當中。")
                pass
        if Config.TWITCH_ACTIVE:
            if self._threadTwitch is None:
                print("啟動 Twitch 直播監聽 ...")
                self._threadTwitch = threading.Thread(target=twitchLive)
                self._threadTwitch.start()
                pass
            else:
                print("Twitch 直播監聽正在運作當中。")
                pass
        if Config.YOUTUBE_ACTIVE:
            if self._threadYoutube is None:
                print("啟動 YouTube 直播監聽 ...")
                self._threadYoutube = threading.Thread(target=youtubeLiveChat)
                self._threadYoutube.start()
                pass
            else:
                print("YouTube 直播監聽正在運作當中。")
                pass
        if Config.DOUYU_ACTIVE:
            if self._threadDouyu is None:
                print("啟動 DouYu 直播監聽 ...")
                self._threadDouyu = threading.Thread(target=douyuLive)
                self._threadDouyu.start()
                pass
            else:
                print("DouYu 直播監聽正在運作當中。")
                pass


def facebookLiveChat(self):
    """"輸出 Facebook 的聊天內容。"""
    url = "https://streaming-graph.facebook.com/" + Config.FACEBOOK_LIVE_VIDEO_ID + "/live_comments?access_token=" + \
        Config.FACEBOOK_ACCESS_TOKEN + \
        "&comment_rate=one_per_two_seconds&fields=from{name,id},message"
    response = with_urllib3(url)
    client = sseclient.SSEClient(response)
    for event in client.events():
        data = json.loads(event.data)
        ssePublish('facebook', data['from']['name'], data['message'])
        if Config.SPEECH_ACTIVE:
            voice.voice(data['message'])


def twitchLive():
    # helix = twitch.Helix(client_id=Config.TWITCH_CLIENT_ID,
    #                      use_cache=True,
    #                      bearer_token=Config.TWITCH_BEARER_TOKEN)
    twitch.Chat(channel=Config.TWITCH_CHANNEL,
                nickname=Config.TWITCH_NICKNAME,
                oauth=Config.TWITCH_OAUTH_TOKEN).subscribe(lambda message: twitchChat(message))
    # oauth=Config.TWITCH_OAUTH_TOKEN).subscribe(lambda message: twitchLive(message, helix))


def twitchChat(data):
    # def twitchLive(data, helix):
    """"輸出 Twitch 的聊天內容。"""
    ssePublish('twitch', data.sender, data.text)
    # author = helix.user(data.sender).display_name
    # publisher.PublisherSingleton._instance.publish('twitch', author, data.text)
    if Config.SPEECH_ACTIVE:
        voice.voice(data.text)


def youtubeLiveChat():
    youtubeChat = youtubeClient(
        Config.YOUTUBE_LIVE_VIDEO_ID,
        processor=CompatibleProcessor())
    while youtubeChat.is_alive():
        try:
            data = youtubeChat.get()
            polling = data['pollingIntervalMillis']/1000
            for chat in data['items']:
                if chat.get('snippet'):
                    ssePublish('youtube',
                        chat['authorDetails']['displayName'],
                        chat['snippet']['displayMessage'])
                    if Config.SPEECH_ACTIVE:
                        voice.voice(chat['snippet']['displayMessage'])
                    time.sleep(polling/len(data['items']))
        except KeyboardInterrupt:
            youtubeChat.terminate()
        except Exception as e:
            print("youtube failed. Exception: %s" % e)


def douyuLive():
    douyu = douyuClient(room_id=Config.DOUYU_ROOM_ID,
                        barrage_host=Config.DOUYU_BARRAGE_HOST)
    douyu.add_handler('chatmsg', douyuChat)
    douyu.start()


def douyuChat(data):
    try:
        ssePublish('douyu', data['nn'], data['txt'])
        if Config.SPEECH_ACTIVE:
            voice.voice(data['txt'])
    except Exception as e:
        print("douyuLiveMessage failed. Exception: %s" % e)


def ssePublish(type, name, message):
    print(f"[{type}] {name}: {message}")
    publish = sseserver.SseServer()
    publish.getInstance().publish(
        json.dumps({
            "channel": type,
            "author": name,
            "message": message,
            "time": time.strftime("%H:%M:%S")
        }))


def randomString(stringLength=8):
    """產生亂數字串。"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def with_urllib3(url):
    """Get a streaming response for the given event feed using urllib3."""
    import urllib3
    http = urllib3.PoolManager()
    return http.request('GET', url, preload_content=False)


def with_requests(url):
    """Get a streaming response for the given event feed using requests."""
    import requests
    return requests.get(url, stream=True)
