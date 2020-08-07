# -*- coding: utf-8 -*-
# __author__ = 'kantai.developer@gmail.com'
# @Time    : 2020/08/07


import os
import time
import random
import string

from config import Config
from playsound import playsound
from xml.etree.ElementTree import Element, SubElement, ElementTree

import azure.cognitiveservices.speech as speechsdk


_now_timestamp = int(time.time())
_now_array = time.localtime(_now_timestamp)
_now_day_string = time.strftime("%Y-%m-%d", _now_array)


def voice(message: str):
    """產生神經語言的聲音檔案。"""
    # azure speech 基本設定
    speech_key, service_region = Config.SPEECH_TOKEN, Config.SPEECH_REGION
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=service_region,
        speech_recognition_language=Config.SPEECH_VOICE_NAME)
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=None)

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
    speak.attrib["version"] = 1.0
    speak.attrib["xmlns"] = 'https://www.w3.org/2001/10/synthesis'
    speak.attrib["xml:lang"] = 'zh-TW'
    voice = SubElement(speak, "voice")
    voice.attrib["name"] = Config.SPEECH_VOICE_NAME
    prosody = SubElement(voice, "prosody")
    prosody.attrib["rate"] = Config.SPEECH_VOICE_PROSODY_RATE
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


if __name__ == '__main__':
    makedirs()
    pass
