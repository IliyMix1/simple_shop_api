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

#Создаём функцию получения сессии
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

async def patch_record(id: int, model, schema, session: AsyncSession):
    #Получаем запись из БД по id(primary key)
    record = await session.get(model, id)

    #Проверяем существует ли такая запись
    if record is None:
        return None
    
    #Находим те столбцы, которые были в запросе и изменяем их(пустые - пропускаем)  
    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(record, key, value)

    #Сохраняем изменения в БД
    await session.commit()
    #Достаём новую запись из БД и кладём её в new_record
    await session.refresh(record)

    return record