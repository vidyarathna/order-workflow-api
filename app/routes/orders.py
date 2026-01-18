"""
Order API routes.
This file defines the FastAPI routes for order management.

Security notes:
- No authentication implemented (would add in production)
- No rate limiting (would add in production)
- Path parameters are validated to prevent invalid inputs
- User input errors return 4xx status codes, not 500
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.models.order import Order, OrderStatus
from app.services.order_service import OrderService

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns the status of the API.
    """
    return {"status": "ok"}

@router.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    Creates an order with the provided details and sets status to CREATED.
    """
    db_order = Order(
        product_id=order.product_id,
        quantity=order.quantity,
        price=order.price,
        status=OrderStatus.CREATED
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get an order by ID.
    Fetches and returns the order with the specified ID.
    """
    if order_id <= 0:
        raise HTTPException(status_code=400, detail="Order ID must be positive")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    """
    Update an order by ID.
    Updates the specified fields of the order.
    """
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = order_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/orders", response_model=list[OrderResponse])
def list_orders(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """
    List orders with pagination.
    Returns a list of orders, limited by limit and offset for performance.
    At scale, this would benefit from database indexes on frequently queried fields.
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be non-negative")
    
    orders = db.query(Order).offset(offset).limit(limit).all()
    return orders

@router.post("/orders/{order_id}/validate")
def validate_order(order_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Start validation of an order in the background.
    Returns immediately with a message, performs validation asynchronously.
    """
    return OrderService.start_validate_order(order_id, background_tasks, db)

@router.post("/orders/{order_id}/approve", response_model=OrderResponse)
def approve_order(order_id: int, db: Session = Depends(get_db)):
    """
    Approve a validated order.
    Transitions the order status from VALIDATED to APPROVED.
    """
    return OrderService.approve_order(order_id, db)

@router.post("/orders/{order_id}/reject", response_model=OrderResponse)
def reject_order(order_id: int, db: Session = Depends(get_db)):
    """
    Reject an order.
    Transitions the order status from CREATED or VALIDATED to REJECTED.
    """
    return OrderService.reject_order(order_id, db)