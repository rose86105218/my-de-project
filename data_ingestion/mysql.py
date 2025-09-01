import pandas as pd
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）
from sqlalchemy import Column, Float, MetaData, String, Table, Integer, Text, DECIMAL, DATETIME
from sqlalchemy.dialects.mysql import insert

from data_ingestion.config import MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT

MYSQL_DATABASE = "AOT"

# 創建元資料
metadata = MetaData()


# 彈幕結構
danmu_table = Table(
    "danmu",  # 資料表名稱
    metadata,
    Column("uploaded_at", DATETIME, nullable=False, comment="資料更新時間"),
    Column("sn", Integer, primary_key=True, comment="彈幕sn"),
    Column("text", String(150), nullable=True, comment="彈幕"),
    Column("userid", String(50), nullable=True, comment="留言者"),
    Column("season", Integer, nullable=True, comment="季"),
    Column("episode", Integer, nullable=True, comment="集"),
    Column("season_episode", Integer, nullable=True, comment="季/集"),
    Column("title", String(100), nullable=True, comment="標題"),
    Column("time", Integer, nullable=True, comment="彈幕所在影片時間"),
)


def upload_data_to_mysql(table_name: str, df: pd.DataFrame, mode: str = "replace"):
    """
    上傳 DataFrame 到 MySQL（使用全域引擎和適當的連接管理）
    """
    mysql_address = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    engine = create_engine(mysql_address)
    
    # ✅ 使用 context manager 確保連接會被正確關閉
    with engine.connect() as connection:
        df.to_sql(
            table_name,
            con=connection,
            if_exists=mode,
            index=False,
        )
    print(f"✅ 資料已上傳到表 '{table_name}'，共 {len(df)} 筆記錄")


def upload_data_to_mysql_upsert(table_obj: Table, data: list[dict]):
    mysql_address = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    engine = create_engine(mysql_address)
    
    # ✅ 自動建立資料表（如果不存在才建立）
    metadata.create_all(engine, tables=[table_obj])

    # upsert
    with engine.begin() as connection:
        for row in data:
            insert_stmt = insert(table_obj).values(**row)
            update_dict = {
                col.name: insert_stmt.inserted[col.name]
                for col in table_obj.columns
            }
            upsert_stmt = insert_stmt.on_duplicate_key_update(**update_dict)
            connection.execute(upsert_stmt)
    print(f"✅ UPSERT 完成，處理 {len(data)} 筆記錄到表 '{table_obj.name}'")
