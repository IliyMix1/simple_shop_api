# Store Backend API
Небольшой REST API для интернет-магазина

## Stack
- Python
- FastAPI 
- PostgreSQL 
- SQLAlchemy Async
- Alembic

## Как запустить проект
1. Клонировать репозиторий:
```bash
git clone https://github.com/IliyMix1/simple_shop_api
```
2. Установить зависимости:
pip install -r requirements.txt
3. Создать .env на основе .env.example
4. Применить миграции(alembic upgrade head)
5. Запустить сервер:
```bash
uvicorn main:app --reload
```

## Основной функционал
- Создание, получение, обновление и удаление товаров
- Создание заказа из списка товаров
- Проверка существования товаров
- Проверка остатков на складе
- Расчёт итоговой стоимости заказа на стороне сервера
- Уменьшение остатков после создания заказа

Проект выполнен как тестовое задание. Основной фокус - структура кода, работа с FastAPI, Pydantic, SQLAlchemy и обработка базовой бизнес логики

## Почему PostgreSQL
В задании в качестве хранилища предлагалась SQLite, однако в этом проекте используется PostgreSQL вместе с асинхронным SQLAlchemy и asyncpg, чтобы показать работу с более приближенным к реальным backend-проектам стеком, а так же в силу наличия у разработчика более обширного опыта работы с этими инструментами


## Структура проекта
```text
simple_shop_api/
├── alembic/              #Миграции базы данных
├── routes/
│   ├── products.py       #Эндпоинты для товаров
│   └── orders.py         #Эндпоинты для заказов
├── database.py           #Подключение к БД и общие функции работы с записями
├── models.py             #SQLAlchemy-модели
├── schemas.py            #Pydantic-схемы
├── main.py               #Точка входа FastAPI-приложения
├── requirements.txt      #Зависимости проекта
├── .env.example          #Пример переменных окружения
└── alembic.ini           #Настройки Alembic
```

## Структура базы данных
В проекте используются три основные таблицы:
### products
Таблица товаров
Поля:

- product_id - первичный ключ товара
- name - название товара, обязательное поле
- description - описание товара, необязательное поле
- price - цена товара
- stock - количество товара на складе

Один товар может встречаться во многих позициях заказа.

### orders
Таблица заказов
Поля:

- order_id - первичный ключ заказа
- total - итоговая стоимость заказа
- status - статус заказа, по умолчанию: created
- created_at - дата и время создания заказа

Итоговая стоимость заказа не передаётся клиентом, а рассчитывается на стороне backend.

### order_items
Таблица позиций заказа
Поля:

- item_id - первичный ключ позиции заказа
- order_id - внешний ключ на заказ
- product_id - внешний ключ на товар
- quantity - количество товара в заказе
- price - цена товара на момент создания заказа

Цена товара сохраняется отдельно в order_items, чтобы заказ хранил актуальную на момент покупки цену, даже если позже цена товара в таблице products изменится.

## Связи между таблицами
* Один заказ может содержать несколько позиций заказа
* Одна позиция заказа относится к одному заказу
* Одна позиция заказа относится к одному товару
* Один товар может встречаться в разных заказах


## Примеры запросов
### Создать товар
```json
curl -X POST "http://127.0.0.1:8000/products/" \
-H "Content-Type: application/json" \
-d '{
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 4500,
  "stock": 10
}'
```
* Пример ответа:
```json
{
  "product_id": 1,
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 4500,
  "stock": 10
}
```

### Получить список товаров
```json
curl -X GET "http://127.0.0.1:8000/products/"
```

* Пример ответа:
```json
[
  {
    "product_id": 1,
    "name": "Keyboard",
    "description": "Mechanical keyboard",
    "price": 4500,
    "stock": 10
  }
]
```

### Получить товар по id
```json
curl -X GET "http://127.0.0.1:8000/products/1"
```
### Обновить товар
```json
curl -X PATCH "http://127.0.0.1:8000/products/1" \
-H "Content-Type: application/json" \
-d '{
  "price": 3990,
  "stock": 15
}'
```
### Удалить товар
```json
curl -X DELETE "http://127.0.0.1:8000/products/1"
```

* Пример ответа:
```json
{
  "message": "Product with id=1 was successfully deleted"
}
```
### Создать заказ
```json
curl -X POST "http://127.0.0.1:8000/orders/" \
-H "Content-Type: application/json" \
-d '{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}'
```
* Пример ответа:
```json
{
  "order_id": 1,
  "total": 9000,
  "status": "created"
}
```
### Получить список заказов
```json
curl -X GET "http://127.0.0.1:8000/orders/"
```
* Пример ответа:
```json
[
  {
    "order_id": 1,
    "total": 9000,
    "status": "created",
    "created_at": "2026-06-25T12:00:00",
    "order_items": [
      {
        "item_id": 1,
        "product_id": 1,
        "product_name": "Keyboard",
        "quantity": 2,
        "price": 4500,
        "subtotal": 9000
      }
    ]
  }
]
```
### Получить заказ по id
```json
curl -X GET "http://127.0.0.1:8000/orders/1"
```

## Основные эндпоинты
### Products
* GET /products/ - Получить список всех товаров
* GET /products/{product_id} - Получить товар по id
* POST /products/ - Создать товар
* PATCH /products/{product_id} - Обновить товар
* DELETE /products/{product_id} - Удалить товар
### Orders
* POST /orders/ - Создать заказ
На вход передаётся список товаров и их количество. Backend проверяет наличие товаров, остатки на складе, рассчитывает итоговую стоимость заказа и уменьшает остатки товаров

* GET /orders/ - Получить список всех заказов
* GET /orders/{order_id} - Получить заказ по id

## Принцип работы ошибок
- 404 Not Found - товар или заказ не найден
- 400 Bad Request - товара недостаточно на складе
- 422 Unprocessable Entity - некорректные входные данные, например отрицательная цена или количество меньше 1