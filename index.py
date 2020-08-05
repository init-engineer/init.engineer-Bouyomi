import io
import os
import json
import time
import flask
import pprint
import random
import string
import twitch
import config
import socket
import sseclient
import azure.cognitiveservices.speech as speechsdk

from pydouyu.client import Client as douyuClient
from pytchat import LiveChat as youtubeClient
from pytchat import CompatibleProcessor
from flask import render_template

from pathlib import Path
from sse import Publisher
from datetime import datetime
from playsound import playsound
from xml.etree.ElementTree import Element, SubElement, ElementTree

import threading


app = flask.Flask(__name__)
publisher = Publisher()


config = config.get("config.json")


_now_timestamp = int(time.time())
_now_array = time.localtime(_now_timestamp)
_now_day_string = time.strftime("%Y-%m-%d", _now_array)

if config.youtube.active:
    youtubeChat = youtubeClient(
        config.youtube.video_id, processor=CompatibleProcessor())


@app.route('/subscribe')
def subscribe():
    return flask.Response(publisher.subscribe(), content_type='text/event-stream')


@app.route('/')
def root():
    ip = flask.request.remote_addr
    publisher.publish('New visit from {} at {}!'.format(ip, datetime.now()))
    return render_template('index.html')


def makedirs():
    """將所需的資料夾建立起來。"""
    if not os.path.exists("./talks"):
        os.makedirs("./talks")
    if not os.path.exists("./talks/voices"):
        os.makedirs("./talks/voices")
    if not os.path.exists("./talks/xmls"):
        os.makedirs("./talks/xmls")
    if not os.path.exists("./talks/voices/" + _now_day_string):
        os.makedirs("./talks/voices/" + _now_day_string)
    if not os.path.exists("./talks/xmls/" + _now_day_string):
        os.makedirs("./talks/xmls/" + _now_day_string)


def facebookLive():
    """"輸出 Facebook 的聊天內容。"""
    url = "https://streaming-graph.facebook.com/" + config.facebook.live_video_id + "/live_comments?access_token=" + \
        config.facebook.access_token + \
        "&comment_rate=one_per_two_seconds&fields=from{name,id},message"
    response = with_urllib3(url)
    client = sseclient.SSEClient(response)
    for event in client.events():
        data = json.loads(event.data)
        print(f"[Facebook] {data['from']['name']}: {data['message']}")
        publisher.publish(json.dumps(
            {"channel": "facebook", "author": data['from']['name'], "message": data['message'], "time": time.strftime("%H:%M:%S")}))
        voice(data['message'])


def twitchLive(data, helix):
    """"輸出 Twitch 的聊天內容。"""
    print(f"[Twitch] {data.sender}: {data.text}")

    author = helix.user(data.sender).display_name

    publisher.publish(json.dumps({"channel": "twitch", "author": author,
                                  "message": data.text, "time": time.strftime("%H:%M:%S")}))
    voice(data.text)


def youtubeLiveMessage():
    """輸出Youtube的聊天內容。"""
    while youtubeChat.is_alive():
        try:
            data = youtubeChat.get()
            polling = data['pollingIntervalMillis']/1000
            for c in data['items']:
                if c.get('snippet'):
                    publisher.publish(json.dumps(
                        {"channel": "youtube", "author": c['authorDetails']['displayName'], "message": c['snippet']['displayMessage'], "time": time.strftime("%H:%M:%S")}))
                    voice(c['snippet']['displayMessage'])
                    time.sleep(polling/len(data['items']))
        except KeyboardInterrupt:
            youtubeChat.terminate()
        except Exception as e:
            print("youtube failed. Exception: %s" % e)


def douyuLiveMessage(data):
    """輸出鬥魚的聊天內容。"""
    try:
        publisher.publish(json.dumps(
            {"channel": "douyu", "author": data['nn'], "message":  data['txt'], "time": time.strftime("%H:%M:%S")}))
        voice(data['txt'])
    except Exception as e:
        print("douyuLiveMessage failed. Exception: %s" % e)


def voice(message: str):
    """產生神經語言的聲音檔案。"""
    # azure speech 基本設定
    speech_key, service_region = config.speech.token, config.speech.region
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region, speech_recognition_language=config.speech.speak.voice.name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=None)

    # 更新時間戳
    _now_timestamp = int(time.time())
    _now_time_string = time.strftime("%H%M%S", _now_array)

    # 建立 XML 檔案並產生聲音檔案、讀取播放
    _file_name = f"{_now_time_string}-{randomString()}"
    build_XAL(message, _file_name)
    ssml_string = open(
        f"./talks/xmls/{_now_day_string}/{_file_name}.xml", "r", encoding="utf-8").read()
    result = speech_synthesizer.speak_ssml_async(ssml_string).get()
    stream = speechsdk.AudioDataStream(result)
    stream.save_to_wav_file(
        f"./talks/voices/{_now_day_string}/{_file_name}.wav")
    playsound(f"./talks/voices/{_now_day_string}/{_file_name}.wav")
    # print("[" + time.strftime("%H:%M:%S", _now_array) + "] " + message)


def build_XAL(message: str, _file_name: str):
    """產生神經語言需要的 XML 檔案。"""
    speak = Element("speak")
    speak.attrib["version"] = config.speech.speak.version
    speak.attrib["xmlns"] = config.speech.speak.xmlns
    speak.attrib["xml:lang"] = config.speech.speak.xmllang
    voice = SubElement(speak, "voice")
    voice.attrib["name"] = config.speech.speak.voice.name
    prosody = SubElement(voice, "prosody")
    prosody.attrib["rate"] = config.speech.speak.voice.prosody.rate
    prosody.text = message
    indent(speak)
    tree = ElementTree(speak)
    tree.write(f"./talks/xmls/{_now_day_string}/{_file_name}.xml",
               encoding="utf-8", xml_declaration=False)


def indent(elem, level=0):
    """將內容縮排。"""
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


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


if __name__ == "__main__":
    makedirs()

    if config.facebook.active:
        __threadFacebook = threading.Thread(target=facebookLive)
        __threadFacebook.start()

    if config.twitch.active:
        helix = twitch.Helix(client_id=config.twitch.client_id,
                             use_cache=True,
                             bearer_token=config.twitch.bearer_token)
        twitch.Chat(channel=config.twitch.channel,
                    nickname=config.twitch.nickname,
                    oauth=config.twitch.token).subscribe(lambda message: twitchLive(message, helix))

    if config.douyu.active:
        douyu = douyuClient(room_id=config.douyu.room_id,
                            barrage_host=config.douyu.barrage_host)
        douyu.add_handler('chatmsg', douyuLiveMessage)
        douyu.start()

    if config.youtube.active:
        __t_youtube = threading.Thread(target=youtubeLiveMessage)
        __t_youtube.start()

    app.run(debug=True, threaded=True)
