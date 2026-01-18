# Dockerfile for Order Workflow API
# Build: docker build -t order-workflow-api .
# Run: docker run -p 8000:8000 order-workflow-api

# Use official Python slim image for smaller size
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Run the application using uvicorn
# Note: SQLite database (orders.db) will be created automatically in the working directory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]