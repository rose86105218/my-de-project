# producer
# 下載所有video_list內的彈幕
from data_ingestion.task_get_danmu import get_danmu, video_list
import pandas as pd

danmu_list = []
for video in video_list:
    task = get_danmu.apply_async(args=[video], queue="get_danmu")
    danmu_partial = task.get()          # 阻塞等待結果
    danmu_list.extend(danmu_partial)    # 用 extend 比 list+list 效率好
    print(f"season{video['season']} episode{video['episode']} 已完成")


# 用pandas轉成DataFrame
danmu_list = pd.DataFrame(danmu_list)


# 匯出成csv
# quoting = 1，代表當資料本身內含逗點時，會在該欄位外再加上逗點，避免被誤分割
danmu_list.to_csv(f"output/danmu.csv",encoding="utf-8", quoting=1)
print("danmu.csv saved.")
