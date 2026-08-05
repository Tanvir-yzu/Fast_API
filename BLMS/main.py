from fastapi import FastAPI
from routers import books

app = FastAPI(
    title="Modern Book Management API",
    version="2.0.0",
    description="A cleanly structured FastAPI application"
)

# Include the books router
app.include_router(books.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Modern FastAPI Book App! Go to /docs for API documentation."}