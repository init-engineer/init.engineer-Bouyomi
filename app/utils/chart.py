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

from . import voice, publisher
from config import Config
from pytchat import CompatibleProcessor
from pytchat import LiveChat as youtubeClient
from pydouyu.client import Client as douyuClient


class Chart():
    if Config.FACEBOOK_ACTIVE:
        print("啟動 Facebook 直播監聽 ...")
        __threadFacebook = threading.Thread(target=facebookLiveChat)
        __threadFacebook.start()
    if Config.TWITCH_ACTIVE:
        print("啟動 Twitch 直播監聽 ...")
        __threadTwitch = threading.Thread(target=twitchLive)
        __threadTwitch.start()
    if Config.YOUTUBE_ACTIVE:
        print("啟動 YouTube 直播監聽 ...")
        __threadYoutube = threading.Thread(target=youtubeLiveChat)
        __threadYoutube.start()
    if Config.DOUYU_ACTIVE:
        print("啟動 DouYu 直播監聽 ...")
        __threadDouyu = threading.Thread(target=douyuLive)
        __threadDouyu.start()


class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


@Singleton
def facebookLiveChat():
    """"輸出 Facebook 的聊天內容。"""
    url = "https://streaming-graph.facebook.com/" + Config.FACEBOOK_LIVE_VIDEO_ID + "/live_comments?access_token=" + \
        Config.FACEBOOK_ACCESS_TOKEN + \
        "&comment_rate=one_per_two_seconds&fields=from{name,id},message"
    response = with_urllib3(url)
    client = sseclient.SSEClient(response)
    for event in client.events():
        data = json.loads(event.data)
        print(f"[Facebook] {data['from']['name']}: {data['message']}")
        publisher.publish('facebook', data['from']['name'], data['message'])
        voice.voice(data['message'])


@Singleton
def twitchChat():
    # helix = twitch.Helix(client_id=Config.TWITCH_CLIENT_ID,
    #                      use_cache=True,
    #                      bearer_token=Config.TWITCH_BEARER_TOKEN)
    twitch.Chat(channel=Config.TWITCH_CHANNEL,
                nickname=Config.TWITCH_NICKNAME,
                oauth=Config.TWITCH_OAUTH_TOKEN).subscribe(lambda message: twitchLive(message))
    # oauth=Config.TWITCH_OAUTH_TOKEN).subscribe(lambda message: twitchLive(message, helix))


def twitchLive(data):
    # def twitchLive(data, helix):
    """"輸出 Twitch 的聊天內容。"""
    print(f"[Twitch] {data.sender}: {data.text}")
    publisher.publish('twitch', data.sender, data.text)
    # author = helix.user(data.sender).display_name
    # publisher.publish('twitch', author, data.text)
    voice.voice(data.text)


@Singleton
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
                    publisher.publish(
                        'youtube',
                        chat['authorDetails']['displayName'],
                        chat['snippet']['displayMessage'])
                    voice.voice(chat['snippet']['displayMessage'])
                    time.sleep(polling/len(data['items']))
        except KeyboardInterrupt:
            youtubeChat.terminate()
        except Exception as e:
            print("youtube failed. Exception: %s" % e)


@Singleton
def douyuLive():
    douyu = douyuClient(room_id=Config.DOUYU_ROOM_ID,
                        barrage_host=Config.DOUYU_BARRAGE_HOST)
    douyu.add_handler('chatmsg', douyuChat)
    douyu.start()


def douyuChat(data):
    try:
        publisher.publish('douyu', data['nn'], data['txt'])
        voice.voice(data['txt'])
    except Exception as e:
        print("douyuLiveMessage failed. Exception: %s" % e)


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


if __name__ == '__main__':
    pass
