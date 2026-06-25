#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas                import CreateProduct, ReadProduct, PatchProduct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy             import select
from database               import get_session, create_record, patch_record
from models                 import Order, Product, OrderItem

product_router = APIRouter(prefix='/products', tags=['Products'])

@product_router.get('/', response_model=list[ReadProduct])
async def get_all_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product)
    )
    return result.scalars().all()

@product_router.get('/{product_id}', response_model=ReadProduct)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product).where(Product.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')
    
    return product

@product_router.post('/', response_model=ReadProduct)
async def create_product(schema: CreateProduct, session: AsyncSession = Depends(get_session)):
    return await create_record(model=Product, schema=schema, session=session)

@product_router.patch('/{product_id}', response_model=ReadProduct)
async def patch_product(product_id: int, schema: PatchProduct, session: AsyncSession = Depends(get_session)):
    product = await patch_record(id=product_id, model=Product, schema=schema, session=session)
    if product is None:
        raise HTTPException(status_code=404, detail='Record not found')
    
    return product

@product_router.delete('/{product_id}')
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product).where(Product.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')
    
    await session.delete(product)
    await session.commit()
    return {'message': f'Product with id={product_id} was successfully deleted'}




