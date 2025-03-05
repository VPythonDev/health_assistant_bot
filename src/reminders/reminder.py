import os

from apscheduler.jobstores.sqlalchemy import \
    SQLAlchemyJobStore  # Хранилище заданий в БД
from apscheduler.schedulers.asyncio import \
    AsyncIOScheduler  # Асинхронный планировщик

url = os.getenv("url")

# 2. Создайте JobStore, указав URL базы данных.
jobstore = SQLAlchemyJobStore(url=url)

# 3. Создайте AsyncIOScheduler, указав JobStore.
scheduler = AsyncIOScheduler(jobstores={'default': jobstore})
