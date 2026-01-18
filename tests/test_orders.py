import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_orders.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override the database dependency to use test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Set up and tear down test database."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=test_engine)

def test_create_order():
    """Test creating a new order."""
    response = client.post("/orders", json={
        "product_id": 1,
        "quantity": 2,
        "price": 15.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == 1
    assert data["quantity"] == 2
    assert data["price"] == 15.0
    assert data["status"] == "CREATED"
    assert "id" in data

def test_list_orders():
    """Test listing orders with pagination."""
    # Create a couple orders first
    client.post("/orders", json={"product_id": 1, "quantity": 1, "price": 10.0})
    client.post("/orders", json={"product_id": 2, "quantity": 2, "price": 20.0})

    response = client.get("/orders?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_list_orders_invalid_params():
    """Test list orders with invalid parameters."""
    response = client.get("/orders?limit=0")
    assert response.status_code == 400

    response = client.get("/orders?offset=-1")
    assert response.status_code == 400
    """Test that invalid workflow transition is blocked."""
    # Create order
    response = client.post("/orders", json={
        "product_id": 1,
        "quantity": 1,
        "price": 10.0
    })
    order_id = response.json()["id"]

    # Try to approve without validating first
    response = client.post(f"/orders/{order_id}/approve")
    assert response.status_code == 400
    assert "Cannot approve" in response.json()["detail"]

def test_reject_order():
    """Test rejecting an order."""
    # Create order
    response = client.post("/orders", json={
        "product_id": 1,
        "quantity": 1,
        "price": 10.0
    })
    order_id = response.json()["id"]

    # Reject the order
    response = client.post(f"/orders/{order_id}/reject")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REJECTED"

def test_validate_order():
    """Test starting validation (background task)."""
    # Create order
    response = client.post("/orders", json={
        "product_id": 1,
        "quantity": 1,
        "price": 10.0
    })
    order_id = response.json()["id"]

    # Start validation
    response = client.post(f"/orders/{order_id}/validate")
    assert response.status_code == 200
    assert response.json() == {"message": "validation started"}

def test_get_nonexistent_order():
    """Test getting an order that doesn't exist."""
    response = client.get("/orders/99999")
    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]

def test_get_order_invalid_id():
    """Test getting an order with invalid ID."""
    response = client.get("/orders/0")
    assert response.status_code == 400
    assert "Order ID must be positive" in response.json()["detail"]