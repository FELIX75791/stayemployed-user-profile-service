from fastapi import FastAPI
from .db import Base, engine
from .routes import user_routes

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Include user-related routes
app.include_router(user_routes.router)