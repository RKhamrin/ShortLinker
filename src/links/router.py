import os
import hashlib
import pytz
import time, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi_cache.decorator import cache

from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from .schemas import LinksCreate
from .models import linking
from models import User

from auth.users import auth_backend, current_active_user, fastapi_users
from auth.db import User

router = APIRouter(
    prefix="/links",
    tags=["links"]
)

def change_time(expires_at):
    """Функция перевода данных из входного формата в формат базы данных

    params: 
        expires_at: datetime (with timezone)

    returns:
        datetime_str: datetime (no timezone)
    """
    dt_naive = expires_at.replace(tzinfo=None)
    datetime_str = dt_naive.strftime("%Y-%m-%d %H:%M:%S.%f")
    datetime_str = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
    return datetime_str

def hash_with_salt(long_link):
    """Функция генерации хэш-функции для замены ссылки 
    Возвращает хэш-функцию с учетом небольшого рандома для исключения 

    params: 
        long_link: str

    returns: 
        hash_object: str
    """
    salt = os.urandom(16)
    hash_object = hashlib.pbkdf2_hmac('sha256', long_link.encode('UTF-8'), salt, 100000)

    return hash_object

@router.post("/shorten")
async def add_link(
    new_link: LinksCreate, 
    session: AsyncSession = Depends(get_async_session)
):
    """Функция создания короткой ссылки
    params:
        user_id: int
        long_link: str
        custom_alias: str (при передаче своей собственной короткой ссылки необходимо указать длину 10)
        expires_at: datetime

    returns: dict
        status: str
        short_link: str
    """
    user_values = new_link.model_dump()
    query = select(linking.c.long_link)
    result = await session.execute(query)
    result = result.scalars().all()

    if len(user_values['custom_alias']) == 10:
        query = select(linking.c.custom_alias)
        result = await session.execute(query)
        result = result.scalars().all()
        if user_values['custom_alias'] in result:
            return {"status": "error", "data": "This alias is already in database. Try another one!"}
    else:

        hash_object = hash_with_salt(long_link=user_values['long_link'])
        user_values['custom_alias'] =  hash_object.hex()[:10]

    table_values = {
        'user_id': user_values['user_id'],
        'long_link': user_values['long_link'],
        'custom_alias': user_values['custom_alias'],
        'expires_at': change_time(user_values['expires_at']),
        'last_usage': datetime.datetime.utcnow(),
        'number_of_usages': 0,
        'is_authorized': True
    }

    statement = insert(linking).values(**table_values)
    await session.execute(statement)
    await session.commit()
    return {"status": "success", "short_link": user_values['custom_alias']}

@router.get("/links/search")
@cache(expire=180)
async def search_link(
    url: str, 
    session: AsyncSession = Depends(get_async_session), 
    status_code=status.HTTP_200_OK
):
    """Функция получения оригинальной ссылки по короткой ссылке 

    params: 
        url: str

    returns: dict
        status: str
        url: str
    """
    query = select(linking.c.custom_alias).where(linking.c.long_link == url)
    result = await session.execute(query)
    result = result.all()
    if len(result) == 0:
        return {"status": "failed", "data": f"no long link {url} in database"}

    return result[0]

@router.get("/{short_code}")
@cache(expire=180)
async def activate_link(
    short_code, 
    session: AsyncSession = Depends(get_async_session)
):
    """Функция перехода на оригинальный сайт по короткой ссылке 

    params: 
        short_code: str

    returns: 
        Redirect
    """
    query = select(linking.c.long_link).where(linking.c.custom_alias == short_code)
    result = await session.execute(query)
    result = result.scalars().all()
    
    if len(result) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="long link not found! check short link")

    query_num_usages = select(linking.c.number_of_usages).where(linking.c.custom_alias == short_code)
    result_num_usages = await session.execute(query_num_usages)
    result_num_usages = result_num_usages.scalars().all()

    statement = update(linking).where(linking.c.custom_alias == short_code).values(
        {"number_of_usages": result_num_usages[0] + 1,
        "last_usage": datetime.datetime.utcnow()}
    )
    await session.execute(statement)
    await session.commit()

    return RedirectResponse(url=result[0], status_code=status.HTTP_301_MOVED_PERMANENTLY)

@router.delete("/{short_code}")
async def delete_link(
    short_code: str, 
    user: User = Depends(current_active_user), 
    session: AsyncSession = Depends(get_async_session)
):
    """Функция удаления информации о короткой ссылке 

    params: 
        short_code: str

    returns: dict
        status: str
    """
    
    statement = delete(linking).where(linking.c.custom_alias == short_code)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}

@router.put("/{short_code}")
async def change_link(
    short_code: str, 
    user: User = Depends(current_active_user), 
    session: AsyncSession = Depends(get_async_session)
):
    """Функция изменения короткой ссылки 

    params: 
        short_code: str

    returns: dict
        status: str
        short_link: str
    """
    
    query = select(linking.c.long_link).where(linking.c.custom_alias == short_code)
    result = await session.execute(query)
    result = result.all()

    if len(result) == 0:
        return {"status": "failed", "data": f"no short link {short_code} in database"}

    hash_object = hash_with_salt(long_link=result[0][0])
    new_short_link = hash_object.hex()[:10]

    statement = update(linking).where(linking.c.custom_alias == short_code).values(
        {"custom_alias": new_short_link}
    )
    await session.execute(statement)
    await session.commit()

    return {"status": "success", "short_link": new_short_link}

@router.get("/{short_code}/stats")
@cache(expire=180)
async def get_statistics_link(
    short_code: str, 
    session: AsyncSession = Depends(get_async_session)
):
    """Функция получения статистик короткой ссылки: оригинальная ссылка, дата создания, количество переходов, дата последнего использования

    params: 
        short_code: str

    returns: dict
        real_link: str
        creation_date: datetime
        number_of_usages: int
        time_of_last_usage: datetime
    """
    query = select(linking).where(linking.c.custom_alias == str(short_code))
    result = await session.execute(query)
    result = result.all()

    if len(result) == 0:
        return {"status": "failed", "data": f"no short link {short_code} in database"}

    return {
        "real link": result[0][2],
        "creation date": result[0][6],
        "number of usages": result[0][7],
        "time of last usage": result[0][5]
    }
