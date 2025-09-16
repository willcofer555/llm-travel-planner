from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from config import settings
from api.routes import chat, trips
from middleware import RateLimitMiddleware, ErrorHandlingMiddleware, LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    logging.info("Application starting up...")
    yield
    logging.info("Application shutting down...")


app = FastAPI(
    title="Travel Location Discovery API",
    description="Backend API for AI-powered travel location discovery",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware in correct order
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware, calls_limit=settings.max_requests_per_minute, time_window=60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(trips.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)