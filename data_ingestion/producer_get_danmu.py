# producer
# 下載所有video_list內的彈幕
from data_ingestion.task_get_danmu import get_danmu

danmu_list = []
for video in video_list:
    danmu_partial = get_danmu.delay(video_list) # delay()代表會由producer提交任務給worker
    danmu_list = danmu_list + danmu_partial
    print("season{} episode{}已完成".format(video["season"], video["episode"]))


# 用pandas轉成DataFrame
danmu_list = pd.DataFrame(danmu_list)


# 匯出成csv
# quoting = 1，代表當資料本身內含逗點時，會在該欄位外再加上逗點，避免被誤分割
danmu_list.to_csv(f"output/danmu.csv",encoding="utf-8", quoting=1)
print("danmu.csv saved.")
