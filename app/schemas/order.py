"""
Pydantic schemas for Order API.
This file defines the request and response models for order operations.
"""
from pydantic import BaseModel, validator
from typing import Optional

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('quantity must be positive')
        return v

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('price must be positive')
        return v

class OrderUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    status: Optional[str] = None

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('quantity must be positive')
        return v

    @validator('price')
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('price must be positive')
        return v

class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    status: str

    class Config:
        from_attributes = True