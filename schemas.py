from typing import Literal
from pydantic import BaseModel, field_validator, Field, model_validator
from datetime import datetime

class CreateProduct(BaseModel):
    name:        str = Field(min_length=2, max_length=100)
    description: str | None = Field(min_length=2, default=None) 
    price:       float = Field(gt=0)  #gt - greater than(больше чем)
    stock:       int   = Field(ge=0)  #ge - greate or equal(больше или равно)

class ReadProduct(BaseModel):
    product_id:  int
    name:        str
    description: str | None
    price:       float
    stock:       int 

class PatchProduct(BaseModel):
    name:        str   | None = None
    description: str   | None = None
    price:       float | None = None
    stock:       int   | None = None


class CreateOrderItem(BaseModel):
    product_id: int 
    quantity:   int = Field(gt=0)  #gt - greater than(больше чем)

class CreateOrder(BaseModel):
    items: list[CreateOrderItem] = Field(min_length=1)