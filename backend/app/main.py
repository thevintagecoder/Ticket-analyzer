from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import models
from .database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Run startup and shutdown logic for the FastAPI application.
    """

    # Create all database tables that do not already exist.
    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="Ticket Analyzer API",
    description="Backend API for the Ticket Analyzer project.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Ticket Analyzer API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Confirm that both FastAPI and PostgreSQL are available.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable",
        ) from error

    return {"status": "ok"}