"""
Order service layer.
This file contains the business logic for order workflow operations.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks
from app.models.order import Order, OrderStatus
from app.db.session import SessionLocal

class OrderService:
    """
    Service class for order workflow operations.
    Handles business rules, validation, and state transitions.
    """

    @staticmethod
    def _is_valid_transition(current_status: str, new_status: str) -> bool:
        """
        Check if a status transition is allowed.
        Workflow rules:
        - CREATED can transition to VALIDATED or REJECTED
        - VALIDATED can transition to APPROVED or REJECTED
        - APPROVED and REJECTED are terminal states
        """
        allowed_transitions = {
            OrderStatus.CREATED: [OrderStatus.VALIDATED, OrderStatus.REJECTED],
            OrderStatus.VALIDATED: [OrderStatus.APPROVED, OrderStatus.REJECTED],
            OrderStatus.APPROVED: [],
            OrderStatus.REJECTED: []
        }
        return new_status in allowed_transitions.get(current_status, [])

    @staticmethod
    def start_validate_order(order_id: int, background_tasks: BackgroundTasks, db: Session):
        """
        Start background validation of an order.
        Checks if validation can be initiated, then triggers background task.
        Returns immediately with a message.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if not OrderService._is_valid_transition(order.status, OrderStatus.VALIDATED):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot validate order in status '{order.status}'. Must be '{OrderStatus.CREATED}'"
            )

        # Trigger background validation
        background_tasks.add_task(OrderService._perform_validation, order_id)
        return {"message": "validation started"}

    @staticmethod
    def _perform_validation(order_id: int):
        """
        Perform order validation in the background.
        Opens its own database session to avoid conflicts.
        Validates order data and updates status accordingly.
        """
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return  # Order was deleted, nothing to do

            # Validate order data
            if order.product_id <= 0 or order.quantity <= 0 or order.price <= 0:
                order.status = OrderStatus.REJECTED
            else:
                order.status = OrderStatus.VALIDATED

            db.commit()
        except Exception:
            # In a real app, log the error
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def approve_order(order_id: int, db: Session) -> Order:
        """
        Approve a validated order.
        Transitions VALIDATED -> APPROVED.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if not OrderService._is_valid_transition(order.status, OrderStatus.APPROVED):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve order in status '{order.status}'. Must be '{OrderStatus.VALIDATED}'"
            )

        order.status = OrderStatus.APPROVED
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def reject_order(order_id: int, db: Session) -> Order:
        """
        Reject an order.
        Transitions CREATED or VALIDATED -> REJECTED.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if not OrderService._is_valid_transition(order.status, OrderStatus.REJECTED):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject order in status '{order.status}'. Must be '{OrderStatus.CREATED}' or '{OrderStatus.VALIDATED}'"
            )

        order.status = OrderStatus.REJECTED
        db.commit()
        db.refresh(order)
        return order