from celery import Celery
import multiprocessing

from data_ingestion.config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    WORKER_USERNAME,
    WORKER_PASSWORD,
)

# print(
#     f"""
#     RABBITMQ_HOST: {RABBITMQ_HOST}
#     RABBITMQ_PORT: {RABBITMQ_PORT}
#     WORKER_USERNAME: {WORKER_USERNAME}
#     WORKER_PASSWORD: {WORKER_PASSWORD}
# """
# )

app = Celery(
    main="worker",
    include=[
        "data_ingestion.tasks",
        "data_ingestion.tasks_crawler_hahow_course",
        "data_ingestion.tasks_crawler_hahow_article",
        "data_ingestion.task_get_danmu",
    ],
    # 指定 broker 為 rabbitmq
    # pyamqp://worker:worker@127.0.0.1:5672/
    broker=f"pyamqp://{WORKER_USERNAME}:{WORKER_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/",
)

print(f"CPU 核心數: {multiprocessing.cpu_count()}")
