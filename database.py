from sqlalchemy             import select
from sqlalchemy.orm         import sessionmaker
from sqlalchemy.pool        import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os
from dotenv import load_dotenv

#Загружаем переменные из .env
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

#Создаём асинхронный движок
engine = create_async_engine(DATABASE_URL)

#Создаём сессию
async_session = sessionmaker(engine, class_=AsyncSession)

#Создаём функции получения сессии
async def get_session():
    #Создаём асинхронную сессию и кладём её в переменную(with - гарантирует, что она сама закроется после работы с сессией)
    async with async_session() as session:
        yield session