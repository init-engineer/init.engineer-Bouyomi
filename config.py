import json
from collections import namedtuple

def get(file):
    try:
        with open(file, encoding='utf-8') as data:
            return json.load(data, object_hook = lambda d: namedtuple('X', d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("命令執行失敗。")
    except FileNotFoundError:
        raise FileNotFoundError("找不到 JSON 檔案。")