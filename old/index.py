import io
import os
import json
import time
import flask
import pprint
import string
import socket
import threading

from pathlib import Path
from config import Config
from datetime import datetime
from flask import render_template

import voice

from sse import Publisher
from makedirs import MakeDirs

publisher = Publisher()


_threadFacebook = None
_threadTwitch = None
_threadYoutube = None
_threadDouyu = None


_now_timestamp = int(time.time())
_now_array = time.localtime(_now_timestamp)
_now_day_string = time.strftime("%Y-%m-%d", _now_array)


# ==============================
# Flask Route
# ==============================


app = flask.Flask(__name__)


@app.route('/')
def index():
    ip = flask.request.remote_addr
    publisher.publish('New visit from {} at {}!'.format(ip, datetime.now()))
    return render_template('index.html')


@app.route('/notify')
def notify():
    return flask.Response(publisher.subscribe(), content_type='text/event-stream')


# ==============================
# 直播平台監聽
# ==============================


def facebookLive(self):
    """"輸出 Facebook 的聊天內容。"""
    import urllib3, sseclient
    url = f"https://streaming-graph.facebook.com/{Config.FACEBOOK_LIVE_VIDEO_ID}/live_comments?access_token={Config.FACEBOOK_ACCESS_TOKEN}&comment_rate=one_per_two_seconds&fields=from{name,id},message"
    http = urllib3.PoolManager()
    response = http.request('GET', url, preload_content=False)
    client = sseclient.SSEClient(response)
    for event in client.events():
        data = json.loads(event.data)
        ssePublish('facebook', data['from']['name'], data['message'])
        if Config.SPEECH_ACTIVE:
            voice.voice(data['message'])


def twitchLive():
    import twitch
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
    from pytchat import CompatibleProcessor, LiveChat as youtubeClient
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
    from pydouyu.client import Client as douyuClient
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


# ==============================
# Custom function
# ==============================


def ssePublish(type, name, message):
    print(f"[{type}] {name}: {message}")
    publisher.publish(
        json.dumps({
            "channel": type,
            "author": name,
            "message": message,
            "time": time.strftime("%H:%M:%S")
        }))


# ==============================
# __name__
# ==============================


if __name__ == "__main__":
    MakeDirs()

    if Config.FACEBOOK_ACTIVE:
        if _threadFacebook is None:
            print("啟動 Facebook 直播監聽 ...")
            _threadFacebook = threading.Thread(target=facebookLive)
            _threadFacebook.start()
            pass
        else:
            print("Facebook 直播監聽正在運作當中。")
            pass
    if Config.TWITCH_ACTIVE:
        if _threadTwitch is None:
            print("啟動 Twitch 直播監聽 ...")
            _threadTwitch = threading.Thread(target=twitchLive)
            _threadTwitch.start()
            pass
        else:
            print("Twitch 直播監聽正在運作當中。")
            pass
    if Config.YOUTUBE_ACTIVE:
        if _threadYoutube is None:
            print("啟動 YouTube 直播監聽 ...")
            _threadYoutube = threading.Thread(target=youtubeLiveChat)
            _threadYoutube.start()
            pass
        else:
            print("YouTube 直播監聽正在運作當中。")
            pass
    if Config.DOUYU_ACTIVE:
        if _threadDouyu is None:
            print("啟動 DouYu 直播監聽 ...")
            _threadDouyu = threading.Thread(target=douyuLive)
            _threadDouyu.start()
            pass
        else:
            print("DouYu 直播監聽正在運作當中。")
            pass

    app.run(debug=True, threaded=True)
