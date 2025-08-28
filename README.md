# de-project
2025 Data Engineering Course Project
>老師原始github： https://github.com/DataEngCamp/de-project



## 資料夾結構
```
de-project/
├── .venv/                                   # Python 虛擬環境
├── .gitignore                               # Git 忽略檔案設定
├── .python-version                          # Python 版本指定
├── README.md                                # 專案說明文件
├── pyproject.toml                           # Python 專案配置檔
├── uv.lock                                  # UV 套件管理鎖定檔
│
├── data_ingestion/                          # 🔥 核心資料擷取模組
│   ├── __init__.py                          # Python 套件初始化
│   ├── config.py                            # 配置檔（環境變數）
│   ├── worker.py                            # Celery Worker 設定
│   ├── tasks.py                             # Celery 任務定義
│   └── producer.py                          # 基本 Producer
│
└── docker-compose-broker.yml               # RabbitMQ Broker 配置
```



## 指令
```
# 建立虛擬環境並安裝依賴（同步）(只需要第一次 & 依賴更新時執行，不用每次開 VS Code 都跑)
uv sync

# 建立一個 network 讓各服務能溝通
docker network create my_network

# 啟動服務
docker compose -f docker-compose-broker.yml up -d

# 停止並移除服務
docker compose -f docker-compose-broker.yml down

＃ 查看服務 logs
docker logs -f rabbitmq
docker logs -f flower

# 啟動 worker
uv run celery -A data_ingestion.worker worker --loglevel=info --concurrency=4 --hostname=worker1@%h -Q get_danmu 
uv run celery -A data_ingestion.worker worker --loglevel=info --concurrency=4 --hostname=worker2@%h -Q get_danmu

--concurrency=4 → 每個 worker 開 4 個 process
--hostname=worker1%h → 設定 worker 名稱，%h是主機名，多台主機時可避免worker名字衝突
-Q get_danmu → 只監控這個 queue

# producer 發送任務
uv run data_ingestion/producer_get_danmu.py

*一般建議先啟動worker，再用producer發送任務
```

## task, producer, worker設定
```
1. task (單一任務單位)
-from data_ingestion.worker import app
-在def()前需要加上@app.task()，用來註冊任務，讓函式可以被celery呼叫

2. producer (丟任務的人)
-from data_ingestion.放置task的py檔名字 import 函式(有用@app.task註冊過的)
需要加上from data_ingestion.tasks_crawler_hahow_course import crawler_hahow_course
-函式.delay("變數")
代表要丟給Celery執行，如：crawler_hahow_course.delay("programing") 

3. worker (接收並執行任務的人)
-在app裡加上有含task的py檔
-注意是含task的py檔，而不是單一task (不然Celery會找不到task位置)，且一個py檔也可能有多個task

app = Celery(
    main="worker",
    include=[
        "data_ingestion.tasks",
        "data_ingestion.tasks_crawler_hahow_course",
        "data_ingestion.tasks_crawler_hahow_article",
    ],
```
