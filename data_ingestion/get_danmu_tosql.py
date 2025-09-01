# task_get_danmu
import requests as req
import json
import pandas as pd
import re
from data_ingestion.worker import app

# 匯入video_list
url = "https://raw.githubusercontent.com/rose86105218/AOT-research/main/video_sn.json"
resp = req.get(url)
video_list = json.loads(resp.text)


def get_danmu(video):
    # 主網頁
    url = "https://api.gamer.com.tw/anime/v1/danmu.php"
    # 影片參數(影片編號，地區等)
    params = {"videoSn": video["video_sn"], "geo": "TW,HK"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"}
    resp = req.get(url, params, headers=headers)

    # 讀取，並轉成json
    content = resp.text
    danmu = json.loads(content)

    #此時data為一個list，[{彈幕1}, {彈幕2}, {彈幕3}]
    data = danmu["data"]["danmu"]

    # 初步資料處理
    # 去除換行、加入集數、加入季、刪除多餘資訊
    cleaned_data = []
    for d in data:
        d["text"] = d["text"].replace("\n","")
        # 刪除標點等
        d["text"] = re.sub(r'[^\w\u4e00-\u9fff/\\]', '', d["text"])
        # 若清理後的彈幕是空白，就跳過不再處理
        if d["text"] == "":
            continue
        #非空白的彈幕
        d["season"] = video["season"]
        d["episode"] = video["episode"]
        d["season_episode"] = video["season_episode"]
        d["title"] = video["title"]
        del d["color"]
        del d["position"]
        del d["size"]
        cleaned_data.append(d)
    return cleaned_data
