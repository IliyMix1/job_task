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

async def create_record(model, schema, session: AsyncSession):
    #Создаём экземля модели в оперативной памяти
    new_record = model(**schema.model_dump()) #Превращаем Pydantic-схему в обычный dict и распаковываем его

    session.add(new_record)
    #Сохраняем изменения в БД
    await session.commit()
    #Достаём новую запись из БД и кладём её в new_record
    await session.refresh(new_record)

    return new_record