import requests as req
import json
import pandas as pd
import re
from datetime import datetime, timezone, timedelta
import time
from data_ingestion.mysql import upload_data_to_mysql, upload_data_to_mysql_upsert, danmu_table



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

    # 此時df包含各則彈幕資訊，包含"text", "userid", "time", "sn"等
    df = pd.DataFrame(danmu["data"]["danmu"])

    # 清理文字
    df["text"] = (
        df["text"]
        .str.replace("\n", "", regex=False)
        .str.replace(r"[^\w\u4e00-\u9fff/\\]", "", regex=True)
    )

    # 去掉空白彈幕
    df = df[df["text"] != ""]

    # 增減欄位
    # 資料取得時間 (+8時區)
    utc_now = datetime.now(timezone.utc)
    df['uploaded_at'] = utc_now.astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    df['uploaded_at'] = pd.to_datetime(df['uploaded_at'])

    df["season"] = video["season"]
    df["episode"] = video["episode"]
    df["season_episode"] = video["season_episode"]
    df["title"] = video["title"]


    df = df.drop(["color", "position", "size"], axis=1)

    #upload_data_to_mysql(table_name="danmu", df=df)

    #先轉成dict
    data = df.to_dict(orient='records')
    upload_data_to_mysql_upsert(table_obj=danmu_table, data=data)
    print(f'第{video["season"]}季,第{video["season_episode"]}集，彈幕已上傳到MySQL')

if __name__ == "__main__":
    for video in video_list:
        get_danmu(video)

# if __name__ == "__main__":
    # get_danmu(video_list[80])