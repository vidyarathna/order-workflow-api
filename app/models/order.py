"""
Order database model.
This file defines the SQLAlchemy model for the Order entity.
"""
from sqlalchemy import Column, Integer, Float, String
from app.db.base import Base

# Order lifecycle states
class OrderStatus:
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, default=OrderStatus.CREATED)