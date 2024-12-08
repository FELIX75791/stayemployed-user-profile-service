from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.routes import user_routes
from app.middleware.logging_middleware import BeforeAfterLoggingMiddleware
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with a list of allowed origins for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Include user-related routes
app.add_middleware(BeforeAfterLoggingMiddleware)
app.include_router(user_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to User Profile Management System"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
