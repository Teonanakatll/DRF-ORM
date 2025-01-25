import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.database.models import Base

from bot.database.orm_query import orm_add_baner_description, orm_creat_categories
from bot.common.texts_for_db import categories, description_for_info_pages

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# создаём бази, echo=True - чтобы выводить все скл запроссы в терминал
engine = create_async_engine(os.getenv('DB_URL'), echo=True)

# bind=engine - указываем движок, class_=AsyncSession - указываем что сессии будут асснтхронные,
# expire_on_commit=False - чтобы сессия сразу не закрывалась
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


#
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_creat_categories(session, categories)
        await  orm_add_baner_description(session, description_for_info_pages)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)