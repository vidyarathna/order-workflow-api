"""
Main FastAPI application.
This file initializes the FastAPI app, includes routers, and creates database tables.
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.routes.orders import router
from app.db.base import Base
from app.db.session import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order & Workflow Management API")

# Jinja2 templates for serving HTML
templates = Jinja2Templates(directory="templates")

# Include order routes
app.include_router(router)

@app.get("/")
def read_root(request: Request):
    """
    Serve the main UI page.
    This is a simple HTML page for testing the API.
    """
    return templates.TemplateResponse("index.html", {"request": request})