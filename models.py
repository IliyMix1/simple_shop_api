from sqlalchemy import Text, BigInteger, DateTime, ForeignKey, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from datetime import datetime

class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = 'orders'

    #Описываем столбцы таблицы
    order_id:   Mapped[int]      = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    total:      Mapped[float]    = mapped_column(Numeric(precision=11, scale=2, asdecimal=False), nullable=False) #Можем пренебречь мелкими погрешностями и чтобы не усложнять жизнь, переводим Numeric во float, а не в Decimal 
    status:     Mapped[str]      = mapped_column(Text, nullable=False, default='created', server_default='created')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    #Описываем связи
    order_items: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='order')

class Product(Base):
    __tablename__ = 'products'

    #Описываем столбцы таблицы
    product_id:  Mapped[int]   = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    name:        Mapped[str]   = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None]   = mapped_column(Text, nullable=True)
    price:       Mapped[float] = mapped_column(Numeric(precision=11, scale=2, asdecimal=False), nullable=False)
    stock:       Mapped[int]   = mapped_column(BigInteger, nullable=False)

    #Описываем связи
    order_items: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='product')

class OrderItem(Base):
    __tablename__ = 'order_items'

    #Описываем столбцы таблицы
    item_id:    Mapped[int]   = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    order_id:   Mapped[int]   = mapped_column(BigInteger, ForeignKey('orders.order_id', ondelete='CASCADE'),     nullable=False)
    product_id: Mapped[int]   = mapped_column(BigInteger, ForeignKey('products.product_id'), nullable=False)
    quantity:   Mapped[int]   = mapped_column(BigInteger, nullable=False)
    price:      Mapped[float] = mapped_column(Numeric(precision=11, scale=2, asdecimal=False), nullable=False,)

    #Описываем связи
    product: Mapped['Product'] = relationship('Product', back_populates='order_items')
    order:   Mapped['Order']   = relationship('Order',   back_populates='order_items')