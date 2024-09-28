from fastapi import FastAPI
from app.db import Base, engine
from app.routes import user_routes
import uvicorn

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Include user-related routes
app.include_router(user_routes.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
