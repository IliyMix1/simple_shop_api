#Импортируем основные зависимости
from fastapi import FastAPI
import uvicorn

#Импортируем роутеры
from routes.products import product_router
from routes.orders   import order_router

#Создаём объект класса
app = FastAPI()

#Добавляем все роутеры
app.include_router(product_router)
app.include_router(order_router)

#Поднимаем сервер
if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)