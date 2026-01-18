# Order Workflow API

A simple FastAPI backend for managing orders with workflow states and background processing.

## Project Overview

This project implements an order management system with basic workflow transitions. It allows creating orders, validating them, approving or rejecting them, and retrieving order details. The system includes a simple web UI for testing and a Docker setup for easy deployment.

**What it solves:** Demonstrates building a REST API with business logic, database persistence, and asynchronous task handling in a single application.

**What it intentionally does NOT do:** It does not handle user authentication, complex business rules, external integrations, or high-scale operations. It's designed for learning and interviews, not production use.

## Architecture Overview

The application follows a layered architecture:

- **Client (Web UI):** Simple HTML interface using Tailwind CSS for testing API endpoints.
- **API Layer (FastAPI):** Handles HTTP requests, input validation, and response formatting.
- **Service Layer:** Contains business logic, workflow rules, and background task coordination.
- **Database Layer (SQLAlchemy + SQLite):** Manages data persistence and transactions.

Each layer has clear responsibilities to separate concerns and make the code easier to understand and test.

## Order Workflow

Orders have four states: CREATED, VALIDATED, APPROVED, REJECTED.

**Allowed transitions:**
- CREATED → VALIDATED (via validation)
- VALIDATED → APPROVED (via approval)
- CREATED → REJECTED (via rejection)
- VALIDATED → REJECTED (via rejection)

Invalid transitions (like APPROVED → anything) return a 400 error. This prevents inconsistent order states and enforces business rules at the API level.

## Background Processing

Validation uses background tasks to simulate asynchronous processing. When you call POST /orders/{id}/validate:

- The API immediately checks if validation can start and returns `{"message": "validation started"}`.
- A background task then performs the actual validation logic and updates the database.

This demonstrates handling long-running operations without blocking the API response. Limitations: Tasks run in the same process, so they're not resilient to app restarts. For production, you'd use a proper task queue.

## Database Design

**Why SQLite:** Chosen for simplicity and zero configuration. The entire database is a single file, making it easy to run locally or in a container.

**Migration to PostgreSQL:** Change the database URL in `app/db/session.py` from `sqlite:///./orders.db` to a PostgreSQL connection string. Update the SQLAlchemy engine accordingly. The models and queries remain the same.

**Transactional consistency:** Each operation (create, validate, etc.) runs in a database transaction. If an error occurs, changes are rolled back to maintain data integrity.

## API Endpoints

- `GET /health` - Health check
- `POST /orders` - Create a new order
- `GET /orders` - List orders with pagination (limit, offset)
- `GET /orders/{order_id}` - Get order details
- `PUT /orders/{order_id}` - Update order fields
- `POST /orders/{order_id}/validate` - Start background validation
- `POST /orders/{order_id}/approve` - Approve a validated order
- `POST /orders/{order_id}/reject` - Reject an order

All endpoints return JSON responses with appropriate HTTP status codes.

## Running the Project

### Local Development
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Access at http://localhost:8000

### Using Docker
```bash
docker build -t order-workflow-api .
docker run -p 8000:8000 order-workflow-api
```
Access at http://localhost:8000

## Testing

Run tests with:

```bash
pip install -r requirements.txt
pytest
```

Tests cover basic order operations and workflow transitions using an isolated test database.

## Design Trade-offs

**Simplifications:**
- Single database file instead of a proper database server
- No authentication or authorization
- In-memory background tasks instead of a queue system
- Basic error handling without detailed logging

**What changes at scale:**
- Replace SQLite with PostgreSQL or similar
- Add proper task queuing (like Celery + Redis)
- Implement authentication and rate limiting
- Add comprehensive logging and monitoring

**Next improvements:**
- Add input validation schemas for all endpoints
- Implement proper error handling with custom exceptions
- Add unit tests for the service layer
- Separate the UI into its own service

## Performance & Security Considerations

**Performance:**
- Added pagination to order listing (limit/offset) to handle large datasets
- Queries are explicit and readable for maintainability
- At scale, database indexes on `id`, `status`, and `created_at` would improve query performance
- No premature optimization - focuses on correctness over speed

**Security:**
- Path parameters are explicitly validated (e.g., positive order IDs)
- User input errors return 4xx status codes, not 500 errors
- Request size is managed by FastAPI's default limits
- No authentication, authorization, or rate limiting implemented (out of scope for this demo)

**What would be added in production:**
- JWT-based authentication and role-based access control
- Rate limiting to prevent abuse
- Input sanitization and validation middleware
- HTTPS enforcement
- Database connection pooling
- Comprehensive logging and monitoring

## Interview Notes

This project demonstrates:
- Building REST APIs with proper separation of concerns
- Implementing business logic in a service layer
- Handling database transactions and consistency
- Using background tasks for non-blocking operations
- Designing simple state machines for workflow management
- Containerizing applications with Docker
- Making trade-offs between simplicity and scalability
- Writing clean, readable code for maintainability