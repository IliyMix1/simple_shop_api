#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas                import CreateOrder, CreateOrderItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm         import joinedload
from sqlalchemy             import select
from database               import get_session, create_record, patch_record
from models                 import Order, Product, OrderItem

order_router = APIRouter(prefix='/orders', tags=['Orders'])

@order_router.post('/')
async def create_order(schema: CreateOrder, session: AsyncSession = Depends(get_session)):
    #Достаём id всех продуктов, переданных пользователем
    product_ids_raw = [item.product_id for item in schema.items]

    #Чтобы избавить от дублирования - сначала первращаем список во множество, а потом обратно
    product_ids = list(set(product_ids_raw))
    #Получаем все записи с нужными product_id
    result = await session.execute(
        select(Product).where(Product.product_id.in_(product_ids))
    )
    products = result.scalars().all()

    #Для удобства составляем словарь {id: продукт}s
    products_by_id = {
        product.product_id: product
        
        for product in products
    }
    
    total = 0

    #Считаем стоимость корзины
    for item in schema.items:
        #Получаем информацию о конкретном продукте из словаря
        product = products_by_id.get(item.product_id)

        #Проверяем существует ли запрошенный продукт
        if product is None:
            raise HTTPException(status_code=404, detail=f'Product with id={item.product_id} not found')
        #Проверяем достаточно ли продукта на складе
        if item.quantity > product.stock:
            raise HTTPException(status_code=400, detail=f'Not enough stock for product with id={item.product_id}')
        
        #Умножаем цену товара на количество товаров
        total += product.price * item.quantity

    #Создаём объект класса Order
    order = Order(total=total)
    #Добавляем объект в текущую сессию, чтобы потом отправить в БД
    session.add(order)
    #Добавляем запись в БД, чтобы получить order_id, однако не завершаем транзакцию
    await session.flush()

    #Добавляем все товары в чек(order_items)
    for item in schema.items:
        #Получаем информацию о конкретном продукте из словаря
        product = products_by_id.get(item.product_id)

        #Подготоваливаем товар для добавления в чек(order_items)
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        #Убираем купленные товары со склада
        product.stock -= item.quantity

        session.add(order_item)

    #Сохраняем все изменения и завершаем транзакцию
    await session.commit()
    await session.refresh(order)
    
    return {
        'order_id': order.order_id,
        'total':    order.total,
        'status':   order.status
    }


@order_router.get('/')
async def get_all_orders(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Order.order_id, Order.total, Order.status, Order.created_at, OrderItem.item_id, OrderItem.product_id, OrderItem.quantity, OrderItem.price, Product.name.label('product_name'))
        .join(OrderItem, Order.order_id == OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.product_id)
        .order_by(Order.order_id)
    )
    rows = result.all()

    orders_by_id = {}
    for row in rows:
        #Если заказ встретился впервые - создаём общую часть заказа.
        if row.order_id not in orders_by_id:
            orders_by_id[row.order_id] = {
                'order_id':    row.order_id,
                'total':       row.total,
                'status':      row.status,
                'created_at':  row.created_at,
                'order_items': []
            }

        #Добавляем текущую позицию в нужный заказ.
        orders_by_id[row.order_id]['order_items'].append({
            'item_id':      row.item_id,
            'product_id':   row.product_id,
            'product_name': row.product_name,
            'quantity':     row.quantity,
            'price':        row.price,
            'subtotal': round(row.price * row.quantity, 2)
        })

    #Нам нужен список заказов, а не словарь с id в качестве ключей
    return list(orders_by_id.values())


@order_router.get('/{order_id}')
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Order.order_id, Order.total, Order.status, Order.created_at, OrderItem.item_id, OrderItem.product_id, OrderItem.quantity, OrderItem.price, Product.name.label('product_name'))
        .join(OrderItem, Order.order_id == OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.product_id)
        .where(Order.order_id == order_id)
    )
    rows = result.all()

    order = build_order_response(rows)

    if order is None:
        raise HTTPException(status_code=404, detail='Order not found')

    return order


def build_order_response(rows):
    '''Вспомогательная функция для форматирования вывода "чека"'''
    if not rows:
        return None
    
    first = rows[0]

    return {
        'order_id':    first.order_id,
        'total':       first.total,
        'status':      first.status,
        'created_at':  first.created_at,
        'order_items': [
            {
                'item_id':      row.item_id,
                'product_id':   row.product_id,
                'product_name': row.product_name,
                'quantity':     row.quantity,
                'price':        row.price,
                'subtotal':     round((row.price * row.quantity), 2)
            }
            for row in rows
        ],
    }