#Импортируем основные зависимости
from fastapi import FastAPI
import uvicorn

#Импортируем роутеры
from routes.common import common_router


#Создаём объект класса
app = FastAPI()


#Добавляем все роутеры
app.include_router(common_router)


#Поднимаем сервер
if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)