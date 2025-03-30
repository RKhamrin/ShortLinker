from celery import Celery
from celery.schedules import crontab
from database import get_async_session
from links.models import linking
import datetime
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import  delete
from datetime import timedelta

celery = Celery('tasks', broker='redis://redis:5370')
celery.conf.beat_schedule = {
    'task-name': {
        'task': 'tasks.tasks.delete_old_links',  # instead 'show'
        # 'schedule': crontab(hour=8, minute=0),
        'schedule': timedelta(seconds=120),
    },
}
celery.conf.timezone = 'UTC'

@celery.task(bind=True)
async def delete_old_links(session: AsyncSession = Depends(get_async_session)):
    now = datetime.datetime.now()
    statement = delete(linking).where(linking.c.expires_at < now)
    print(2)

    await session.execute(statement)
    await session.commit()
    # print({"status": "success"})
    return {"status": "success"}

