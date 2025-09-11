"""
get_danmu 爬蟲 DAG
爬取彈幕並上傳至 MySQL 資料庫
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

# 導入爬蟲任務
from data_ingestion.get_danmu_tosql import get_danmu, video_list


# 定義要爬取的分類
CATEGORIES = [
    "programming", "marketing", "language", "design",
    "lifestyle", "music", "art", "photography", 'humanities',
    "finance-and-investment", "career-skills", "cooking",
]

# 預設參數
default_args = {
    'owner': 'data-team',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,  # 失敗時重試 2 次
    'retry_delay': timedelta(minutes=1),  # 重試間隔 5 分鐘
    'execution_timeout': timedelta(hours=1),  # 執行超時時間 1 小時
}



# 建立 DAG
with DAG(
    dag_id='get_danmu_tosql_dag',
    default_args=default_args,
    description='爬取巴哈動畫瘋彈幕DAG - 爬取進擊的巨人',
    schedule_interval='0 23 * * *',  # 每天 23 點執行
    catchup=False,  # 不執行歷史任務
    max_active_runs=1,  # 同時只允許一個 DAG 實例運行
    tags=['danmu', 'crawler', 'etl'],
) as dag:

    # 開始任務
    start_task = BashOperator(
        task_id='start_crawler',
        bash_command='echo "開始執行彈幕爬蟲任務..."',
    )


    # 產生1~5季分流 (把task_id存在字典) season_branch = {1: season_branch_1, 2: season_branch_2, ...}
    season_branches = {}
    for i in range(1, 6):
        season_branch[i] = DummyOperator(
            task_id=season_branch_{i},
        )


    # 還沒弄好 做成字典，task要每季一個list
    # get_danmu_task = {1:[task1, task2, ...], 2: [taskn, taskm, ...]}
    # 文章爬取任務 - 為每個分類創建單獨的任務
    get_danmu_tasks = {}
    for i in range(1, 6):
        get_danmu_tasks[i] = []
        for video in video_list[video_list["season"]==i]:
            task = PythonOperator(
                task_id=f'get_danmu_{video["episode"]}',
                python_callable=get_danmu,
                op_args=[video["episode"]],
            )
            get_danmu_tasks[i].append(task)

    # 結束任務
    end_task = BashOperator(
        task_id='end_crawler',
        bash_command='echo "彈幕爬蟲任務執行完成！"',
        trigger_rule='all_success',  # 只有當所有前置任務成功時才執行
    )

    # 設定任務依賴關係
    # 開始 -> 環境驗證 -> 兩個分流 -> 各自的爬取任務 -> 結束
    for i in range(1, 6):
        start_task >> season_branch[i] >> get_danmu_tasks[i] >> end_task
